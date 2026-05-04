# Backend — Daily Productivity Planner

FastAPI service with SQLAlchemy + Alembic + PostgreSQL.

## Setup

1. Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set `DATABASE_URL` and `PROJECT_ROOT`.

3. Run migrations:

```bash
alembic upgrade head
```

4. (Optional) Load sample data:

```bash
python scripts/seed_sample.py
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs
