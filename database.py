## Database Integration for Financial Document Analyzer
## Uses SQLAlchemy with SQLite (can be swapped for PostgreSQL)

import os
import uuid
import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

## Database URL - SQLite for local, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

## Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

## Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

## Base class
Base = declarative_base()


## Analysis Result Model
class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, processing, success, failed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


## Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)


## Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


## Save new analysis to database
def save_analysis(db, filename: str, query: str) -> AnalysisResult:
    analysis = AnalysisResult(
        id=str(uuid.uuid4()),
        filename=filename,
        query=query,
        status="pending",
        created_at=datetime.datetime.utcnow()
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


## Update analysis result in database
def update_analysis(db, analysis_id: str, result: str = None, status: str = "success", error: str = None):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if analysis:
        analysis.result = result
        analysis.status = status
        analysis.error = error
        analysis.completed_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(analysis)
    return analysis


## Get analysis by ID
def get_analysis(db, analysis_id: str) -> AnalysisResult:
    return db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()


## Get all analyses
def get_all_analyses(db, limit: int = 10) -> list:
    return db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).limit(limit).all()
