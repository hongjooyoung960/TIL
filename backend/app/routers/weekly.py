from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import WeeklyStatsRead
from ..services.stats_service import sleep_pattern_series, weekly_summary

router = APIRouter(prefix="/weekly", tags=["weekly"])


@router.get("/sleep-pattern/recent")
def sleep_recent(db: Session = Depends(get_db)):
    return sleep_pattern_series(db, days_back=14)


@router.get("/{year}/{week}", response_model=WeeklyStatsRead)
def get_week(year: int, week: int, db: Session = Depends(get_db)):
    data = weekly_summary(db, year, week)
    return WeeklyStatsRead(**data)
