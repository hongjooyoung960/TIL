"""Insert demo daily plan, activities, and goals if database is empty."""

from __future__ import annotations

import os
import sys
from datetime import date, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from app.services.report_service import write_daily_reports
from app.services.stats_service import recalculate_daily_plan_scores


def seed(db: Session) -> None:
    if db.query(models.Goal).count() > 0:
        print("Seed skipped: goals already exist.")
        return

    long_term = models.Goal(
        title="건강과 커리어 균형 잡기",
        description="장기적으로 지속 가능한 루틴 확립",
        goal_type="long_term",
        parent_goal_id=None,
        target_date=date(2027, 12, 31),
        status="active",
        progress=25,
    )
    db.add(long_term)
    db.flush()

    weekly = models.Goal(
        title="이번 주 딥워크 20시간",
        description="집중 블록 확보",
        goal_type="weekly",
        parent_goal_id=long_term.id,
        target_date=None,
        status="active",
        progress=40,
    )
    db.add(weekly)
    db.flush()

    plan_day = date(2026, 5, 4)
    plan = models.DailyPlan(
        plan_date=plan_day,
        wake_time=time(6, 30),
        sleep_time=time(23, 15),
        main_goal="핵심 기능 MVP 완료",
        daily_memo="포트폴리오용 데모 데이터",
    )
    db.add(plan)
    db.flush()

    acts = [
        models.Activity(
            daily_plan_id=plan.id,
            activity_name="아침 계획 정리",
            category="routine",
            start_time=time(7, 0),
            end_time=time(7, 30),
            duration_minutes=30,
            status="done",
            importance_score=3,
            focus_score=4,
            memo="커피 포함",
        ),
        models.Activity(
            daily_plan_id=plan.id,
            activity_name="백엔드 API 마무리",
            category="deep_work",
            start_time=time(9, 0),
            end_time=time(12, 0),
            duration_minutes=180,
            status="done",
            importance_score=5,
            focus_score=5,
            memo=None,
        ),
        models.Activity(
            daily_plan_id=plan.id,
            activity_name="프런트 주간 차트 구현",
            category="deep_work",
            start_time=time(13, 0),
            end_time=time(15, 30),
            duration_minutes=150,
            status="partial",
            importance_score=4,
            focus_score=4,
            memo="일부 컴포넌트만 완료",
        ),
        models.Activity(
            daily_plan_id=plan.id,
            activity_name="러닝 30분",
            category="health",
            start_time=None,
            end_time=None,
            duration_minutes=30,
            status="missed",
            importance_score=2,
            focus_score=3,
            memo="비 와서 스킵",
        ),
    ]
    db.add_all(acts)

    db.add(
        models.DailyGoalLink(
            daily_plan_id=plan.id,
            goal_id=weekly.id,
            contribution_score=5,
        )
    )

    db.commit()

    recalculate_daily_plan_scores(db, plan.id)
    try:
        write_daily_reports(db, plan_day)
    except Exception as exc:
        print("Report generation skipped:", exc)


def main():
    db = SessionLocal()
    try:
        seed(db)
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
