#!/usr/bin/env python3
"""Generate daily JSON/Markdown reports and run git add/commit/push.

Loads backend services from `backend/` (same repo layout as production).

Usage:
  python scripts/git_auto_commit.py --date 2026-05-04

Requires DATABASE_URL and PROJECT_ROOT (see backend/.env.example).
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

os.chdir(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()

    plan_day = date.fromisoformat(args.date)

    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env")
    if not os.getenv("PROJECT_ROOT"):
        os.environ["PROJECT_ROOT"] = str(ROOT)

    from app.database import SessionLocal
    from app.services.git_service import commit_daily_git

    db = SessionLocal()
    try:
        result = commit_daily_git(db, plan_day)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
