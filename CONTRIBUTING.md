# Team Contribution Guide

Welcome to the team! To maintain code quality, architecture consistency, and smooth deployments, please review and follow this contribution guide.

---

## 1. Git & Branching Strategy
We use a structured branch naming strategy to organize our pipeline. **Direct commits to `main` are strictly prohibited.** All changes must be made in branch-based isolates and submitted via Pull Requests.

### Branch Naming Conventions
* **Features**: `feature/<module-name>` (e.g. `feature/forecasting-api`, `feature/uploads-ui`)
* **Bug Fixes**: `bugfix/<issue-name>` (e.g. `bugfix/db-connection-retry`)
* **Hot Fixes**: `hotfix/<description>` (e.g. `hotfix/cors-origin-fix`)

---

## 2. Development Workflow

### Step 1: Pull the Latest Changes
Before starting any new task, sync your local workspace with the main branch:
```bash
git checkout main
git pull origin main
```

### Step 2: Create a Feature Branch
Spin up your working branch using the appropriate convention:
```bash
git checkout -b feature/my-feature-name
```

### Step 3: Implement & Test
Make sure your implementations are fully validated. Always check:
* Run backend tests: `pytest` inside the `backend` directory.
* Run frontend build checks: `npm run build` inside the `frontend` directory.

### Step 4: Keep Branches Clean
Commit frequently with clear messages. When pushed, open a Pull Request (PR) on GitHub against the `main` branch.

### Step 5: Pull Requests (PR)
All PRs require at least one approving review and must pass all automated status checks (linting, tests, build) before merging.

---

## 3. Commit Message Format
We follow the **Conventional Commits** format to generate clear changelogs:
`<type>(<scope>): <short summary>`

### Types
* `feat`: A new feature.
* `fix`: A bug fix.
* `docs`: Documentation changes only.
* `style`: Styling changes that do not affect the logic (formatting, spaces).
* `refactor`: Code changes that neither fix a bug nor add a feature.
* `test`: Adding missing tests or correcting existing tests.
* `chore`: Maintenance tasks, dependencies updates, etc.

### Examples
* `feat(forecasting): add Prophet training runner script`
* `fix(auth): correct token extraction header validation`
* `docs(readme): add docker build run instruction steps`

---

## 4. Coding Standards
* **Python**:
  - Follow PEP 8 guidelines.
  - Maintain type hints where possible.
  - Document public classes and functions.
* **JavaScript / React**:
  - Avoid inline CSS styling. Define custom styles inside `index.css` or component stylesheet files.
  - Keep components modular, focused, and reusable.
* **Architecture Freeze**:
  - The Phase 2 System Design is frozen.
  - No contributor may modify architectural decisions without explicit approval.
  - Feature implementation must follow the frozen architecture.
  - Do NOT modify the 5-tier architecture paths without explicit approval.
  - Do NOT bypass the ML/Worker division: Web servers handle API gateways only; background execution and math models run inside the worker process and ML packages respectively.

---

## 5. Docker Integration Guide
Containers are the standard running environment for local development and staging.
* **Local Runs**: You may run Python and Node services directly on the host machine for fast inspection.
* **Integrations**: For end-to-end flow checks, use Docker Compose:
  ```bash
  docker compose up --build
  ```
* **Hot Reloading**: Bind mounts are configured inside `docker-compose.yml`. Modifying source files on your host machine will immediately sync and hot-reload inside the running containers.
* **Port Mappings**:
  - React Client: `5173`
  - FastAPI App: `8000`
  - MongoDB Engine: `27017`
  - Python Worker: No ports exposed.
