from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..models import Activity
from ..schemas import ActivityCreate, ActivityRead, ActivityUpdate
from ..services.report_service import write_daily_reports
from ..services.stats_service import recalculate_daily_plan_scores

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityRead)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    plan = crud.get_daily_plan_by_id(db, payload.daily_plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    act = crud.create_activity(db, payload)
    recalculate_daily_plan_scores(db, act.daily_plan_id)
    plan_date = plan.plan_date
    try:
        write_daily_reports(db, plan_date)
    except Exception:
        pass
    return act


@router.put("/{activity_id}", response_model=ActivityRead)
def update_activity(activity_id: str, payload: ActivityUpdate, db: Session = Depends(get_db)):
    from uuid import UUID

    uid = UUID(activity_id)
    existing = db.query(Activity).filter(Activity.id == uid).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Activity not found")
    act = crud.update_activity(db, uid, payload)
    recalculate_daily_plan_scores(db, act.daily_plan_id)
    plan = crud.get_daily_plan_by_id(db, act.daily_plan_id)
    if plan:
        try:
            write_daily_reports(db, plan.plan_date)
        except Exception:
            pass
    return act


@router.delete("/{activity_id}")
def delete_activity(activity_id: str, db: Session = Depends(get_db)):
    from uuid import UUID

    uid = UUID(activity_id)
    existing = db.query(Activity).filter(Activity.id == uid).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Activity not found")
    pid = existing.daily_plan_id
    ok = crud.delete_activity(db, uid)
    recalculate_daily_plan_scores(db, pid)
    plan = crud.get_daily_plan_by_id(db, pid)
    if plan:
        try:
            write_daily_reports(db, plan.plan_date)
        except Exception:
            pass
    return {"deleted": ok}
