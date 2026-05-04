from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from .. import crud
from ..models import DailyPlan
from .stats_service import achievement_rates_for_plan


def project_root() -> Path:
    import os

    env = os.getenv("PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[3]


def build_daily_payload(db: Session, plan: DailyPlan) -> dict[str, Any]:
    basic, weighted = achievement_rates_for_plan(plan)
    acts = []
    for a in sorted(plan.activities, key=lambda x: x.created_at):
        acts.append(
            {
                "id": str(a.id),
                "activity_name": a.activity_name,
                "category": a.category,
                "start_time": a.start_time.isoformat() if a.start_time else None,
                "end_time": a.end_time.isoformat() if a.end_time else None,
                "duration_minutes": a.duration_minutes,
                "status": a.status,
                "importance_score": a.importance_score,
                "focus_score": a.focus_score,
                "memo": a.memo,
            }
        )
    linked = []
    db.refresh(plan)
    for link in plan.goal_links:
        g = crud.get_goal(db, link.goal_id)
        linked.append(
            {
                "goal_id": str(link.goal_id),
                "title": g.title if g else None,
                "contribution_score": link.contribution_score,
            }
        )

    completed = sum(1 for x in plan.activities if x.status == "done")
    missed = sum(1 for x in plan.activities if x.status == "missed")

    return {
        "date": plan.plan_date.isoformat(),
        "wake_time": plan.wake_time.isoformat() if plan.wake_time else None,
        "sleep_time": plan.sleep_time.isoformat() if plan.sleep_time else None,
        "main_goal": plan.main_goal,
        "daily_memo": plan.daily_memo,
        "achievement_rate_weighted": weighted,
        "achievement_rate_basic": basic,
        "activities": acts,
        "linked_goals": linked,
        "summary_stats": {
            "activity_count": len(acts),
            "completed_count": completed,
            "missed_count": missed,
            "total_score_basic": float(plan.total_score) if plan.total_score is not None else basic,
        },
    }


def write_daily_reports(db: Session, plan_date: date) -> tuple[Path, Path]:
    plan = crud.get_daily_plan_by_date(db, plan_date)
    if not plan:
        raise ValueError(f"No daily plan for {plan_date}")

    root = project_root()
    daily_dir = root / "daily"
    reports_dir = root / "reports"
    daily_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    ds = plan_date.isoformat()
    json_path = daily_dir / f"{ds}.json"
    md_path = reports_dir / f"{ds}-report.md"

    payload = build_daily_payload(db, plan)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    cat_summary: dict[str, int] = {}
    completed_lines: list[str] = []
    missed_lines: list[str] = []
    for row in payload["activities"]:
        cat = row.get("category") or "uncategorized"
        cat_summary[cat] = cat_summary.get(cat, 0) + 1
        line = f"- {row['activity_name']} ({row['status']})"
        if row["status"] == "done":
            completed_lines.append(line)
        elif row["status"] == "missed":
            missed_lines.append(line)

    md = "\n".join(
        [
            f"# Daily report — {ds}",
            "",
            f"- **Main goal**: {payload.get('main_goal') or '_none_'}",
            f"- **Wake**: {payload.get('wake_time') or '_n/a_'}",
            f"- **Sleep**: {payload.get('sleep_time') or '_n/a_'}",
            f"- **Achievement (weighted)**: {payload.get('achievement_rate_weighted')}%",
            f"- **Achievement (basic)**: {payload.get('achievement_rate_basic')}%",
            "",
            "## Completed activities",
            "\n".join(completed_lines) if completed_lines else "_none_",
            "",
            "## Missed activities",
            "\n".join(missed_lines) if missed_lines else "_none_",
            "",
            "## Category summary",
            "\n".join(f"- {k}: {v} activities" for k, v in sorted(cat_summary.items())),
            "",
            "## Memo",
            payload.get("daily_memo") or "_none_",
            "",
        ]
    )
    md_path.write_text(md, encoding="utf-8")
    return json_path, md_path
