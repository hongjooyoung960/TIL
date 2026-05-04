from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import DailyPlanCreate, DailyPlanRead, DailyPlanUpdate
from ..services.report_service import write_daily_reports
from ..services.stats_service import recalculate_daily_plan_scores

router = APIRouter(prefix="/daily", tags=["daily"])


def _parse_date(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format") from exc


@router.post("", response_model=DailyPlanRead)
def create_daily(payload: DailyPlanCreate, db: Session = Depends(get_db)):
    if crud.get_daily_plan_by_date(db, payload.plan_date):
        raise HTTPException(status_code=409, detail="Plan already exists for this date")
    plan = crud.create_daily_plan(db, payload)
    recalculate_daily_plan_scores(db, plan.id)
    plan = crud.get_daily_plan_by_date(db, payload.plan_date)
    try:
        write_daily_reports(db, payload.plan_date)
    except Exception:
        pass
    return plan


@router.get("/{date}", response_model=DailyPlanRead)
def get_daily(date: str, db: Session = Depends(get_db)):
    d = _parse_date(date)
    plan = crud.get_daily_plan_by_date(db, d)
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    return plan


@router.put("/{date}", response_model=DailyPlanRead)
def update_daily(date: str, payload: DailyPlanUpdate, db: Session = Depends(get_db)):
    d = _parse_date(date)
    plan = crud.update_daily_plan(db, d, payload)
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    recalculate_daily_plan_scores(db, plan.id)
    plan = crud.get_daily_plan_by_date(db, d)
    try:
        write_daily_reports(db, d)
    except Exception:
        pass
    return plan


@router.delete("/{date}")
def delete_daily(date: str, db: Session = Depends(get_db)):
    d = _parse_date(date)
    ok = crud.delete_daily_plan(db, d)
    if not ok:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    return {"deleted": True}
