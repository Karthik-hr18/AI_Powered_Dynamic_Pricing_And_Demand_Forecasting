# pyrefly: ignore [missing-import]
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.ml import get_artifact_loader

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML artifacts once on startup and cache in memory
    loader = get_artifact_loader()
    loader.load_all()
    yield

app = FastAPI(
    title="AI-Powered Dynamic Pricing & Demand Forecasting Platform",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/health")
def read_health():
    return {"status": "ok"}
