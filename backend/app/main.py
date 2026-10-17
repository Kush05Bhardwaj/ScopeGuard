from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.agreements import router as agreements_router
from app.api.reports import router as reports_router

app = FastAPI(
    title="ScopeGuard Local API",
    description="Local-first AI scope analysis for freelancers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(agreements_router)
app.include_router(analysis_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {"name": "ScopeGuard Local API", "version": "0.1.0", "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "scopeguard-api", "mode": "local"}
