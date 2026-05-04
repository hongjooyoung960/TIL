from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from . import models
from .schemas import (
    ActivityCreate,
    ActivityUpdate,
    DailyGoalLinkCreate,
    DailyPlanCreate,
    DailyPlanUpdate,
    GoalCreate,
    GoalUpdate,
)


def get_daily_plan_by_date(db: Session, plan_date: date) -> models.DailyPlan | None:
    return (
        db.query(models.DailyPlan)
        .options(
            joinedload(models.DailyPlan.activities),
            joinedload(models.DailyPlan.goal_links),
        )
        .filter(models.DailyPlan.plan_date == plan_date)
        .first()
    )


def get_daily_plan_by_id(db: Session, plan_id: UUID) -> models.DailyPlan | None:
    return (
        db.query(models.DailyPlan)
        .options(
            joinedload(models.DailyPlan.activities),
            joinedload(models.DailyPlan.goal_links),
        )
        .filter(models.DailyPlan.id == plan_id)
        .first()
    )


def create_daily_plan(db: Session, data: DailyPlanCreate) -> models.DailyPlan:
    plan = models.DailyPlan(
        plan_date=data.plan_date,
        wake_time=data.wake_time,
        sleep_time=data.sleep_time,
        main_goal=data.main_goal,
        daily_memo=data.daily_memo,
    )
    db.add(plan)
    db.flush()
    for link in data.goal_links:
        db.add(
            models.DailyGoalLink(
                daily_plan_id=plan.id,
                goal_id=link.goal_id,
                contribution_score=link.contribution_score,
            )
        )
    db.commit()
    db.refresh(plan)
    return get_daily_plan_by_date(db, plan.plan_date)  # type: ignore[return-value]


def update_daily_plan(
    db: Session, plan_date: date, data: DailyPlanUpdate
) -> models.DailyPlan | None:
    plan = get_daily_plan_by_date(db, plan_date)
    if not plan:
        return None
    for field in ("wake_time", "sleep_time", "main_goal", "daily_memo"):
        val = getattr(data, field)
        if val is not None:
            setattr(plan, field, val)
    if data.goal_links is not None:
        db.query(models.DailyGoalLink).filter(
            models.DailyGoalLink.daily_plan_id == plan.id
        ).delete(synchronize_session=False)
        for link in data.goal_links:
            db.add(
                models.DailyGoalLink(
                    daily_plan_id=plan.id,
                    goal_id=link.goal_id,
                    contribution_score=link.contribution_score,
                )
            )
    db.commit()
    return get_daily_plan_by_date(db, plan_date)


def delete_daily_plan(db: Session, plan_date: date) -> bool:
    plan = get_daily_plan_by_date(db, plan_date)
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True


def create_activity(db: Session, data: ActivityCreate) -> models.Activity:
    act = models.Activity(**data.model_dump())
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


def update_activity(db: Session, activity_id: UUID, data: ActivityUpdate) -> models.Activity | None:
    act = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not act:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(act, k, v)
    db.commit()
    db.refresh(act)
    return act


def delete_activity(db: Session, activity_id: UUID) -> bool:
    act = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not act:
        return False
    db.delete(act)
    db.commit()
    return True


def list_goals(db: Session) -> list[models.Goal]:
    return db.query(models.Goal).order_by(models.Goal.created_at.asc()).all()


def get_goal(db: Session, goal_id: UUID) -> models.Goal | None:
    return db.query(models.Goal).filter(models.Goal.id == goal_id).first()


def create_goal(db: Session, data: GoalCreate) -> models.Goal:
    g = models.Goal(**data.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def update_goal(db: Session, goal_id: UUID, data: GoalUpdate) -> models.Goal | None:
    g = get_goal(db, goal_id)
    if not g:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(g, k, v)
    db.commit()
    db.refresh(g)
    return g


def delete_goal(db: Session, goal_id: UUID) -> bool:
    g = get_goal(db, goal_id)
    if not g:
        return False
    db.delete(g)
    db.commit()
    return True


def daily_plans_in_week(db: Session, year: int, week: int) -> list[models.DailyPlan]:
    """ISO calendar week."""
    plans = (
        db.query(models.DailyPlan)
        .options(
            joinedload(models.DailyPlan.activities),
            joinedload(models.DailyPlan.goal_links),
        )
        .order_by(models.DailyPlan.plan_date.asc())
        .all()
    )
    return [p for p in plans if p.plan_date.isocalendar()[:2] == (year, week)]


def list_git_logs(db: Session, limit: int = 50) -> list[models.GitCommitLog]:
    return (
        db.query(models.GitCommitLog)
        .order_by(models.GitCommitLog.created_at.desc())
        .limit(limit)
        .all()
    )


def add_git_log(
    db: Session,
    *,
    plan_date: date,
    status: str,
    commit_hash: str | None = None,
    commit_message: str | None = None,
    error_message: str | None = None,
) -> models.GitCommitLog:
    row = models.GitCommitLog(
        plan_date=plan_date,
        commit_hash=commit_hash,
        commit_message=commit_message,
        status=status,
        error_message=error_message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
