# System Architecture

**Version**: 1.0  
**Current Status**: Phase 3  
**Milestone**: M1 Complete  

---

This document provides a summary of the implemented architecture, repository layout, and design conventions for the AI-Powered Dynamic Pricing & Demand Forecasting Platform.

---

## 1. Project Overview
The platform is designed to provide real-time dynamic pricing recommendations and demand forecasts by joining sales data, inventory limits, and machine learning models. It isolates operations into distinct frontend, backend, database, and machine learning modules.

---

## 2. Technology Stack
The platform uses the following stack:
* **Frontend**: React + Vite (JS), Styled with custom CSS.
* **Backend**: FastAPI (Python), asynchronous handling, Motor (MongoDB driver), Pydantic (data parsing/settings).
* **Worker Process**: Isolated Python module sharing the backend codebase, executing asynchronous background jobs.
* **ML Layer**: Separate Python module using `scikit-learn`, `xgboost`, `prophet`, `scipy`, `pandas`, `numpy`.
* **Database**: MongoDB (v7.0) for document store and data persistence.
* **Containerization**: Docker & Docker Compose.

---

## 3. Repository Structure

```
├── backend/                  # FastAPI Application Workspace
│   ├── app/                  # Application source
│   │   ├── core/             # Base configurations (middleware, db, logging)
│   │   │   ├── db/
│   │   │   └── middleware/
│   │   ├── domains/          # Domain-driven feature directories
│   │   │   ├── admin/
│   │   │   ├── anomaly/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── forecasting/
│   │   │   ├── inventory/
│   │   │   ├── pricing/
│   │   │   ├── products/
│   │   │   ├── sales_data/
│   │   │   └── uploads/
│   │   ├── worker/           # Background job queue processing entrypoint
│   │   └── main.py           # FastAPI Web Application entrypoint
│   ├── tests/                # Automated pytest suites
│   ├── Dockerfile            # Python environment Docker setup
│   ├── pyproject.toml        # Poetry/pip metadata configuration
│   └── requirements.txt      # Backend, ML, and test dependencies
│
├── frontend/                 # Vite-React Application Workspace
│   ├── src/
│   │   ├── features/         # Feature-specific components and logic
│   │   ├── shared/           # Common components, layouts, hooks, API client
│   │   ├── routes/           # Routing layout and components
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # React app mount script
│   │   └── index.css         # Custom CSS (Obsidian Glassmorphic theme)
│   ├── Dockerfile            # Node environment Docker setup
│   └── package.json          # Node package definition
│
├── ml/                       # Machine Learning Codebase (Independent module)
│   ├── forecasting/          # Forecasting training, inference, and evaluation
│   ├── pricing/              # Pricing simulation and candidates optimization
│   ├── anomaly/              # Spike and drop anomaly engine
│   └── shared/               # Shared ML utilities
│
├── docs/                     # Static documentation resources
└── docker-compose.yml        # Multi-container local orchestration layout
```

---

## 4. Docker Architecture & Topology
The platform is orchestrated locally using a series of isolated containers:

```
                  ┌──────────────────────┐
                  │   Browser (Host)     │
                  └──────────┬───────────┘
                             │ (Port 5173)
                             ▼
                  ┌──────────────────────┐
                  │   pricing_frontend   │ (Node 22)
                  └──────────┬───────────┘
                             │ (Port 8000 API)
                             ▼
┌────────────────────────────────────────────────────────┐
│                    platform_net (Bridge Network)       │
│                                                        │
│   ┌───────────────────┐        ┌───────────────────┐   │
│   │  pricing_backend  │        │  pricing_worker   │   │
│   │   (FastAPI App)   │        │ (Background Proc) │   │
│   └─────────┬─────────┘        └─────────┬─────────┘   │
│             │                            │             │
│             └──────────────┬─────────────┘             │
│                            │ (Internal port 27017)     │
│                            ▼                           │
│                 ┌──────────────────────┐               │
│                 │    pricing_mongo     │ (Mongo 7)     │
│                 └──────────┬───────────┘               │
└────────────────────────────┼───────────────────────────┘
                             ▼
                     [mongo_data Volume]
```

* **Frontend**: Accessible at `localhost:5173`. Uses bind-mounts and polling configuration inside `vite.config.js` for Windows hot-reloading.
* **Backend**: Accessible at `localhost:8000`. Exposes `/` and `/health` endpoints.
* **Worker**: Shares the backend Docker image but overrides the entrypoint to run the queue consumer.
* **Database**: MongoDB v7.0 instance, storing data inside the persistent volume `mongo_data`. Includes a `mongosh` healthcheck.

---

## 5. High-Level Milestones & Status

| Milestone | Description | Status |
| :--- | :--- | :--- |
| **M1** | Project Initialization & Docker Setup | **Completed** |
| **M2** | Database Models & Migrations | Planned |
| **M3** | Authentication & Authorization API | Planned |
| **M4** | Products & Inventory Management API | Planned |
| **M5** | CSV Data Upload Pipeline | Planned |
| **M6** | Baseline Forecasting Pipeline | Planned |
| **M7** | Pricing Logic & Candidates Evaluator | Planned |
| **M8** | Anomaly Detection Engine | Planned |
| **M9** | Background Job Queue (Worker) | Planned |
| **M10** | Admin Control Dashboard Backend | Planned |
| **M11** | Shared Layout & Navigation Frontend | Planned |
| **M12** | Auth & Product Feature UI | Planned |
| **M13** | Forecasting & Anomaly Dashboard UI | Planned |
| **M14** | Pricing Simulation UI | Planned |
| **M15** | Integration, E2E Testing & Deployment | Planned |
