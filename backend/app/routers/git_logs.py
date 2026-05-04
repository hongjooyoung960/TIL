from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import GitCommitLogRead
from ..services.git_service import commit_daily_git

router = APIRouter(prefix="/git", tags=["git"])


def _parse_date(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format") from exc


@router.post("/commit-daily/{date}")
def commit_daily(date: str, db: Session = Depends(get_db)):
    d = _parse_date(date)
    plan = crud.get_daily_plan_by_date(db, d)
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found for commit")
    result = commit_daily_git(db, d)
    return result


@router.get("/logs", response_model=list[GitCommitLogRead])
def git_logs(db: Session = Depends(get_db)):
    return crud.list_git_logs(db)
