from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid

from crewai import Crew, Process
from agents import financial_analyst, verifier
from task import analyze_financial_document, verification
from database import init_db, get_db, save_analysis, update_analysis, get_analysis, get_all_analyses

app = FastAPI(title="Financial Document Analyzer")

## Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """To run the whole crew"""
    financial_crew = Crew(
        agents=[verifier, financial_analyst],
        tasks=[verification, analyze_financial_document],
        process=Process.sequential,
    )
    result = financial_crew.kickoff({'query': query, 'file_path': file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    use_queue: bool = Form(default=False),
    db: Session = Depends(get_db)
):
    """
    Analyze financial document and provide comprehensive investment recommendations.
    - use_queue=False (default): Synchronous analysis, waits for result
    - use_queue=True: Asynchronous analysis via Celery queue, returns task_id
    """

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        ## Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        ## Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        ## Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        ## Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        ## Save to database
        analysis = save_analysis(db, filename=file.filename, query=query.strip())

        ## Use Celery queue for async processing
        if use_queue:
            try:
                from celery_worker import analyze_document_task
                task = analyze_document_task.delay(
                    query=query.strip(),
                    file_path=file_path,
                    analysis_id=analysis.id
                )
                return {
                    "status": "queued",
                    "task_id": task.id,
                    "analysis_id": analysis.id,
                    "message": "Document queued for analysis. Use /status/{analysis_id} to check result."
                }
            except Exception:
                pass

        ## Synchronous processing
        response = run_crew(query=query.strip(), file_path=file_path)

        ## Update database with result
        update_analysis(db, analysis.id, result=str(response), status="success")

        return {
            "status": "success",
            "analysis_id": analysis.id,
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except HTTPException:
        raise
    except Exception as e:
        if 'analysis' in locals():
            update_analysis(db, analysis.id, status="failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

    finally:
        if not use_queue and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@app.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """Check the status of an analysis by ID"""
    analysis = get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "analysis_id": analysis.id,
        "filename": analysis.filename,
        "query": analysis.query,
        "status": analysis.status,
        "result": analysis.result,
        "error": analysis.error,
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at
    }


@app.get("/analyses")
async def list_analyses(limit: int = 10, db: Session = Depends(get_db)):
    """Get list of all recent analyses"""
    analyses = get_all_analyses(db, limit=limit)
    return {
        "total": len(analyses),
        "analyses": [
            {
                "analysis_id": a.id,
                "filename": a.filename,
                "query": a.query,
                "status": a.status,
                "created_at": a.created_at,
                "completed_at": a.completed_at
            }
            for a in analyses
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
