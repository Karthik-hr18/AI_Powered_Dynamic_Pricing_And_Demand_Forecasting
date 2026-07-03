# pyrefly: ignore [missing-import]
from fastapi import FastAPI

app = FastAPI(title="AI-Powered Dynamic Pricing & Demand Forecasting Platform")

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/health")
def read_health():
    return {"status": "ok"}
