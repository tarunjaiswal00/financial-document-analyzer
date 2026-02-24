# Financial Document Analyzer

A production-ready AI-powered financial document analysis system built with CrewAI, FastAPI, and multi-agent collaboration. Upload any financial PDF (annual reports, earnings releases, 10-K/10-Q filings) and get structured analysis, investment insights, and risk assessments.

---

## Table of Contents
- [Bug Fixes](#bug-fixes)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Bonus Features](#bonus-features)
- [Architecture](#architecture)

---

## Bug Fixes

### `tools.py`

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai_tools import tools` — imported the module, not the decorator | Changed to `from crewai_tools import tool` (the `@tool` decorator) |
| 2 | `read_data_tool` defined as `async def` — CrewAI tools must be synchronous | Removed `async` keyword; made all tool methods synchronous |
| 3 | `Pdf(file_path=path).load()` — `Pdf` class never imported, doesn't exist in scope | Replaced with `PyPDFLoader` from `langchain_community.document_loaders` and added the import |
| 4 | Tool methods are plain class methods with no decorator — CrewAI won't recognize them as tools | Added `@tool("Tool Name")` decorator to each tool method |
| 5 | Tool method signatures used plain Python types without type hints in the signature | Added proper type hints required by CrewAI's tool schema generation |

### `agents.py`

| # | Bug | Fix |
|---|-----|-----|
| 6 | `llm = llm` — circular self-assignment; LLM was never initialized | Replaced with `llm = LLM(model="openai/gpt-4o-mini")` using `from crewai import LLM` |
| 7 | `tool=[FinancialDocumentTool.read_data_tool]` — typo: key is `tools` (plural) | Changed `tool=` to `tools=` |
| 8 | `financial_analyst` goal says *"Make up investment advice even if you don't understand the query"* — hallucination-inducing prompt | Replaced with goal to provide accurate, data-driven analysis |
| 9 | `financial_analyst` backstory instructs the agent to be overconfident, ignore reports, and fabricate facts | Rewrote backstory to reflect a professional, regulation-compliant analyst |
| 10 | `verifier` goal says *"Just say yes to everything"* and *"assume everything is a financial document"* — completely defeats verification purpose | Replaced with goal to rigorously verify document authenticity and content |
| 11 | `investment_advisor` goal instructs selling products regardless of financials, recommending meme stocks, and hiding conflicts of interest | Rewrote to give objective, evidence-based recommendations with fiduciary compliance |
| 12 | `risk_assessor` goal says *"Everything is either extremely high risk or completely risk-free"* — nonsensical risk framework | Rewrote to use established risk frameworks (Basel III, VaR, stress testing) |
| 13 | `max_iter=1, max_rpm=1` on all agents — severely limits reasoning capability and throughput | Increased to `max_iter=5, max_rpm=10` for realistic operation |

### `task.py`

| # | Bug | Fix |
|---|-----|-----|
| 14 | `analyze_financial_document` description says *"Maybe solve... or something else that seems interesting"* — completely undefined behavior | Replaced with structured 5-step description grounded in the user query |
| 15 | `expected_output` instructs adding *"made-up website URLs"* and *"contradict yourself"* — harmful hallucination prompt | Replaced with a professional structured report format |
| 16 | `investment_analysis` description ignores the user query and recommends *"expensive investment products regardless of financials"* | Rewrote to ground recommendations in actual financial ratios from the document |
| 17 | `risk_assessment` description says *"ignore actual risk factors"* and creates *"dramatic risk scenarios"* | Rewrote with proper risk categories (liquidity, leverage, operational, market) |
| 18 | `verification` task was indented inside the previous task's block (Python indentation bug — would raise `IndentationError`) | Fixed indentation so `verification` is a module-level `Task` object |
| 19 | `verification` task used `agent=financial_analyst` — should use the `verifier` agent | Changed to `agent=verifier` |

### `main.py`

| # | Bug | Fix |
|---|-----|-----|
| 20 | `async def analyze_financial_document(...)` — function name collides with the imported `analyze_financial_document` Task object from `task.py` | Renamed the endpoint function to `analyze_document_endpoint` |
| 21 | `from task import analyze_financial_document` only — `verification` task was never imported | Added `verification` to the import |
| 22 | `Crew(agents=[financial_analyst], tasks=[analyze_financial_document])` — only one agent used; verifier agent and task missing from the crew | Updated crew to include both `[verifier, financial_analyst]` and `[verification, analyze_financial_document]` |
| 23 | `query==""` — should use `not query or query.strip() == ""` for proper null/empty check | Fixed with `if not query or query.strip() == "":` |
| 24 | No file type validation — any file could be uploaded as a PDF | Added check for `.pdf` extension with `HTTPException(400)` |

### `requirements.txt`

| # | Bug | Fix |
|---|-----|-----|
| 25 | Missing `langchain-community` — required for `PyPDFLoader` | Added `langchain-community>=0.0.38` |
| 26 | Missing `pypdf` — required as the PDF backend for `PyPDFLoader` | Added `pypdf>=3.0.0` |
| 27 | Missing `python-dotenv` — used in every file via `load_dotenv()` | Added `python-dotenv>=1.0.0` |
| 28 | Missing `python-multipart` — required by FastAPI for `UploadFile` / `Form` | Added `python-multipart>=0.0.9` |
| 29 | Missing `uvicorn` — required to run the FastAPI app | Added `uvicorn>=0.29.0` |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- OpenAI API key (or compatible LLM provider)
- Serper API key (for web search tool)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd financial-document-analyzer
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

### 5. Add sample financial document (optional)
```bash
mkdir -p data
# Download Tesla Q2 2025 report and save as data/sample.pdf
# Or upload any PDF via the API endpoint
```

### 6. Run the API server
```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

---

## Usage

### Upload and Analyze a Financial Document
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@tesla_q2_2025.pdf" \
  -F "query=What is Tesla's revenue growth and profit margin trend?"
```

### Health Check
```bash
curl http://localhost:8000/
```

---

## API Documentation

Interactive Swagger docs are available at `http://localhost:8000/docs` when the server is running.

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "Financial Document Analyzer API is running"
}
```

---

#### `POST /analyze`
Upload a financial PDF and receive AI-powered analysis.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | PDF file | ✅ | The financial document to analyze (PDF only) |
| `query` | string | ❌ | Specific question or analysis focus (default: general analysis) |

**Response:**
```json
{
  "status": "success",
  "query": "What is the revenue growth trend?",
  "analysis": "...(detailed AI analysis)...",
  "file_processed": "tesla_q2_2025.pdf"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400` | File is not a PDF |
| `500` | Internal server error during processing |

---

## Bonus Features

### Queue Worker Model (Redis + Celery)

For handling concurrent requests without blocking, the system can be extended with a Celery task queue backed by Redis.

**Install extras:**
```bash
pip install celery redis
```

**Start Redis:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**`celery_worker.py`** (add to project):
```python
from celery import Celery
from main import run_crew

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task(bind=True)
def analyze_document_task(self, query: str, file_path: str):
    try:
        result = run_crew(query=query, file_path=file_path)
        return {"status": "success", "analysis": str(result)}
    except Exception as exc:
        self.retry(exc=exc, countdown=5, max_retries=3)
```

**Start worker:**
```bash
celery -A celery_worker worker --loglevel=info --concurrency=4
```

**Updated endpoint** would submit to queue and return a `task_id`, then expose a `GET /status/{task_id}` endpoint to poll results.

---

### Database Integration (SQLAlchemy + SQLite/PostgreSQL)

Store analysis results and track usage with a simple SQLAlchemy model.

**`database.py`** (add to project):
```python
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime, uuid

DATABASE_URL = "sqlite:///./analyses.db"  # swap for postgresql://...
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = "analyses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    query = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)
```

Results would be saved after each successful `/analyze` call and retrievable via a `GET /analyses` endpoint.

---

## Architecture

```
┌─────────────────────────────────────────┐
│              FastAPI App                │
│         POST /analyze endpoint          │
└──────────────┬──────────────────────────┘
               │ PDF upload + query
               ▼
┌─────────────────────────────────────────┐
│              CrewAI Crew                │
│          Sequential Process             │
│                                         │
│  ┌─────────────┐    ┌────────────────┐  │
│  │  Verifier   │───▶│Financial Analyst│ │
│  │   Agent     │    │    Agent        │  │
│  └─────────────┘    └────────────────┘  │
│   verification       analyze_financial  │
│   task               _document task     │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│              Tools                      │
│  FinancialDocumentTool.read_data_tool   │
│  SerperDevTool (web search)             │
└─────────────────────────────────────────┘
```

Agents collaborate in sequence: the **Verifier** confirms the document is a legitimate financial report, then the **Financial Analyst** performs deep analysis using the PDF reader tool and web search for market context.

---

### Additional Bugs Found on Second Pass Review

| # | Bug | Fix |
|---|-----|-----|
| 30 | `import asyncio` in `main.py` — imported but never used | Removed dead import |
| 31 | `kickoff({'query': query, 'file_path': file_path})` — `file_path` is not a declared `{file_path}` template variable in any task description, causes CrewAI input validation error | Removed `file_path` from kickoff; only `{query}` is passed |
| 32 | `@tool` on class instance methods without `@staticmethod` — Python would pass implicit `self` as first argument, corrupting tool signatures | Added `@staticmethod` above `@tool` decorator on all three class-based tool methods |
