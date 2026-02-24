## Celery Worker for Financial Document Analyzer
## Handles concurrent requests using Redis as message broker
## This allows multiple PDF analyses to run simultaneously

import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

## Redis connection URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

## Create Celery app
celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL
)

## Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # One task per worker at a time
    task_soft_time_limit=300,      # 5 minutes soft limit
    task_time_limit=360,           # 6 minutes hard limit
)


@celery_app.task(bind=True, max_retries=3)
def analyze_document_task(self, query: str, file_path: str, analysis_id: str):
    """
    Celery task to analyze financial document asynchronously.
    
    Args:
        query (str): User's analysis query
        file_path (str): Path to the uploaded PDF file
        analysis_id (str): Database ID to update with results
        
    Returns:
        dict: Analysis result with status
    """
    from crewai import Crew, Process
    from agents import financial_analyst, verifier
    from task import analyze_financial_document, verification
    from database import SessionLocal, update_analysis

    db = SessionLocal()

    try:
        ## Update status to processing
        update_analysis(db, analysis_id, status="processing")

        ## Run the CrewAI crew
        financial_crew = Crew(
            agents=[verifier, financial_analyst],
            tasks=[verification, analyze_financial_document],
            process=Process.sequential,
        )

        result = financial_crew.kickoff({
            'query': query,
            'file_path': file_path
        })

        ## Update database with success result
        update_analysis(
            db,
            analysis_id,
            result=str(result),
            status="success"
        )

        return {
            "status": "success",
            "analysis_id": analysis_id,
            "result": str(result)
        }

    except Exception as exc:
        ## Update database with error
        update_analysis(
            db,
            analysis_id,
            status="failed",
            error=str(exc)
        )

        ## Retry the task up to 3 times
        raise self.retry(exc=exc, countdown=10, max_retries=3)

    finally:
        db.close()

        ## Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
