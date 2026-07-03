# AI-Powered Dynamic Pricing & Demand Forecasting Platform

**Current Phase**: Phase 3 — Implementation  
**Current Milestone**: M1 — Completed  

---

Welcome to the AI-Powered Dynamic Pricing & Demand Forecasting Platform. This platform leverages modern machine learning forecasting (Prophet, XGBoost) and heuristics-based optimization to adjust prices dynamically based on demand patterns, inventory limits, and anomaly triggers.

---

## Tech Stack
* **Frontend**: React + Vite, customized CSS styling.
* **Backend**: FastAPI, Motor (MongoDB Async), Pydantic Settings.
* **Worker Process**: Custom background task worker.
* **Machine Learning**: NumPy, Pandas, Scikit-learn, XGBoost, Prophet, SciPy.
* **Database**: MongoDB 7.0.
* **Orchestration**: Docker, Docker Compose.

---

## Repository Structure

```
├── backend/                  # FastAPI & Python Worker Environment
├── frontend/                 # React & Vite Development Environment
├── ml/                       # Machine Learning Training & Inference Scripts
└── docs/                     # Platform Documentation & Specifications
```

---

## Current Status
* **Scaffolding**: Completed. The 5-tier folder structure, init modules, and configuration blueprints match the specifications.
* **FastAPI Backend**: Scaffolded base web server with health endpoints.
* **Vite React Frontend**: Scaffolded landing page presenting dynamic glassmorphic animations and system readiness checking.
* **Containerization**: Full Docker integration completed with bridge network security, health checks, and hot-reload bind mounts.

---

## Prerequisites
Ensure the following tools are installed locally:
* **Python**: 3.12 or 3.13
* **Node.js**: v22+
* **Docker / Docker Compose** (Optional for local running, required for container run)

---

## Environment Setup

### 1. Backend Config
Copy the configuration template:
```bash
cp backend/.env.example backend/.env
```
Fill in the development credentials locally. Key variables:
* `MONGODB_URL`: Connection string (use `mongodb://localhost:27017/pricing_platform` locally, or let Docker map it to `mongodb://mongo:27017/pricing_platform`).
* `JWT_SECRET`: Token signature key.

### 2. Frontend Config
Copy the configuration template:
```bash
cp frontend/.env.example frontend/.env
```

---

## How to Run Locally (Host Machine)

### 1. Run Backend Web Server
Navigate to the `backend` directory, activate the environment, and execute:
```bash
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Verify the server by opening `http://localhost:8000/` and `http://localhost:8000/health`.

### 2. Run Background Worker
With the virtual environment active in `backend/`:
```bash
python -m app.worker.main
```

### 3. Run Frontend App
Navigate to the `frontend` directory and install/run:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## How to Run Using Docker (Container Orchestration)

Start the environment with Docker Compose:
```bash
# Build and boot the stack
docker compose up --build

# Run in detached mode (background)
docker compose up -d

# Stop and tear down the stack
docker compose down -v
```
Services:
* **Frontend**: `http://localhost:5173` (Includes hot-reloading using polling mounts).
* **Backend**: `http://localhost:8000`
* **Mongo**: `localhost:27017`

---

## Branch Strategy & Workflow
Our branch structure is managed strictly:
* **Feature Branches**: `feature/<module>` (e.g., `feature/auth`, `feature/anomaly`)
* **Bug Fixes**: `bugfix/<issue-name>`
* **Hot Fixes**: `hotfix/<description>`

All contributions must follow our contribution guide in `CONTRIBUTING.md`. Never commit directly to `main`.

---

## Road Map (High-level Milestones)
* **M1**: Project Scaffolding (Completed)
* **M2**: Database Foundation
* **M3**: Authentication
* **M4**: CSV Upload & Ingestion
* **M5**: Preprocessing Pipeline
* **M6**: ML Pipelines
* **M7**: Inventory Risk
* **M8**: Dashboard APIs
* **M9**: Frontend Auth
* **M10**: Upload UI
* **M11**: Dashboard UI
* **M12**: Product Detail
* **M13**: Admin
* **M14**: Testing
* **M15**: Deployment

---

## License
Licensed under the [MIT License](LICENSE) (Placeholder).
