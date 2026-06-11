from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api import eval, jobs, reports, research
from app.db import Base, engine

app = FastAPI(title="ResearchFlow AI API", version="1.0.0")
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(eval.router, prefix="/api/eval", tags=["eval"])

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/health")
def healthcheck():
    return {"status": "ok", "app": "ResearchFlow AI", "version": "1.0.0"}

@app.get("/", response_class=FileResponse)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
