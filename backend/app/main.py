import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import activities, daily, git_logs, goals, reports, weekly

load_dotenv()

app = FastAPI(title="Daily Productivity Planner API", version="0.1.0")

# Comma-separated list, e.g. "https://app.example.com" or "https://app.example.com,http://localhost:5173"
# SPA on a single origin: set to that origin only (scheme + host + optional port).
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(daily.router)
app.include_router(activities.router)
app.include_router(weekly.router)
app.include_router(goals.router)
app.include_router(git_logs.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}


