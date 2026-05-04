from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any

from sqlalchemy.orm import Session

from .. import crud
from ..models import DailyPlan


def _time_to_minutes(t: time | None) -> float | None:
    if t is None:
        return None
    return t.hour * 60 + t.minute + t.second / 60.0


def minutes_to_time_str(m: float | None) -> str | None:
    if m is None:
        return None
    total = int(round(m))
    h, mn = divmod(total, 60)
    return f"{h:02d}:{mn:02d}"


def achievement_rates_for_plan(plan: DailyPlan) -> tuple[float | None, float | None]:
    """Returns (basic_rate, weighted_rate) as percentages."""
    acts = list(plan.activities)
    total = len(acts)
    if total == 0:
        return None, None

    done = [a for a in acts if a.status == "done"]
    completed_count = len(done)
    basic = (completed_count / total) * 100.0

    weights_all = sum(max(a.importance_score, 1) for a in acts)
    weights_done = sum(max(a.importance_score, 1) for a in done)
    weighted = (weights_done / weights_all) * 100.0 if weights_all else None

    return round(basic, 2), round(weighted, 2) if weighted is not None else None


def recalculate_daily_plan_scores(db: Session, plan_id: Any) -> DailyPlan | None:
    plan = (
        db.query(DailyPlan).filter(DailyPlan.id == plan_id).first()
    )
    if not plan:
        return None
    basic, weighted = achievement_rates_for_plan(plan)
    plan.total_score = basic
    plan.achievement_rate = weighted
    db.commit()
    db.refresh(plan)
    return plan


def weekly_summary(db: Session, year: int, week: int) -> dict[str, Any]:
    plans = crud.daily_plans_in_week(db, year, week)

    rates: list[float] = []
    achievement_by_day: list[dict[str, Any]] = []
    total_focus = 0.0
    total_duration = 0.0
    category_minutes: dict[str, float] = {}
    missed = 0
    wake_minutes: list[float] = []
    sleep_minutes: list[float] = []

    for p in sorted(plans, key=lambda x: x.plan_date):
        acts = list(p.activities)
        day_basic, day_weighted = achievement_rates_for_plan(p)
        if day_weighted is not None:
            rates.append(float(day_weighted))
        achievement_by_day.append(
            {
                "date": p.plan_date.isoformat(),
                "achievement_rate": day_weighted,
                "basic_rate": day_basic,
            }
        )

        if p.wake_time:
            wm = _time_to_minutes(p.wake_time)
            if wm is not None:
                wake_minutes.append(wm)
        if p.sleep_time:
            sm = _time_to_minutes(p.sleep_time)
            if sm is not None:
                sleep_minutes.append(sm)

        for a in acts:
            dur = float(a.duration_minutes or 0)
            if dur <= 0 and a.start_time and a.end_time:
                sm = _time_to_minutes(a.start_time)
                em = _time_to_minutes(a.end_time)
                if sm is not None and em is not None:
                    dur = max(0.0, em - sm)

            cat = a.category or "uncategorized"
            if a.status == "done":
                total_focus += dur * float(a.focus_score)
            total_duration += dur
            if a.status == "done" or a.status == "partial":
                category_minutes[cat] = category_minutes.get(cat, 0.0) + dur
            if a.status == "missed":
                missed += 1

    avg_rate = sum(rates) / len(rates) if rates else None
    avg_wake = sum(wake_minutes) / len(wake_minutes) if wake_minutes else None
    avg_sleep = sum(sleep_minutes) / len(sleep_minutes) if sleep_minutes else None

    return {
        "year": year,
        "week": week,
        "average_achievement_rate": round(avg_rate, 2) if avg_rate is not None else None,
        "total_focused_time_minutes": round(total_focus, 2),
        "total_activity_duration_minutes": round(total_duration, 2),
        "category_distribution": {k: round(v, 2) for k, v in category_minutes.items()},
        "average_wake_time": minutes_to_time_str(avg_wake),
        "average_sleep_time": minutes_to_time_str(avg_sleep),
        "missed_activity_count": missed,
        "achievement_by_day": achievement_by_day,
    }


def sleep_pattern_series(db: Session, days_back: int = 14) -> list[dict[str, Any]]:
    """Recent daily wake/sleep for line chart."""
    end = date.today()
    start = end - timedelta(days=days_back)
    plans = (
        db.query(DailyPlan)
        .filter(DailyPlan.plan_date >= start, DailyPlan.plan_date <= end)
        .order_by(DailyPlan.plan_date.asc())
        .all()
    )
    out = []
    for p in plans:
        out.append(
            {
                "date": p.plan_date.isoformat(),
                "wake_minutes": _time_to_minutes(p.wake_time),
                "sleep_minutes": _time_to_minutes(p.sleep_time),
            }
        )
    return out
