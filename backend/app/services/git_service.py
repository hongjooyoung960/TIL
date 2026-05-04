from __future__ import annotations

import os
import subprocess
from datetime import date

from sqlalchemy.orm import Session

from .. import crud
from .report_service import write_daily_reports


def _run_git(args: list[str], cwd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def commit_daily_git(db: Session, plan_date: date) -> dict[str, str | None]:
    """Generate artifacts, git add/commit/push. Never raises — returns status dict."""
    branch = os.getenv("GIT_BRANCH", "main")
    remote = os.getenv("GIT_REMOTE", "origin")

    write_daily_reports(db, plan_date)
    ds = plan_date.isoformat()
    root = os.getenv("PROJECT_ROOT")
    if not root:
        from pathlib import Path

        root = str(Path(__file__).resolve().parents[3])

    json_rel = f"daily/{ds}.json"
    md_rel = f"reports/{ds}-report.md"

    add = _run_git(["git", "add", json_rel, md_rel], cwd=root)
    if add.returncode != 0:
        msg = (add.stderr or add.stdout or "").strip()
        crud.add_git_log(
            db,
            plan_date=plan_date,
            status="failed",
            error_message=f"git add failed: {msg}",
        )
        return {"status": "failed", "error": msg}

    commit_msg = f"daily log: {ds}"
    commit = _run_git(["git", "commit", "-m", commit_msg], cwd=root)
    out = (commit.stderr or commit.stdout or "").strip()

    # Nothing to commit is exit 1 — treat as soft failure but informative
    if commit.returncode != 0 and "nothing to commit" not in out.lower():
        crud.add_git_log(
            db,
            plan_date=plan_date,
            status="failed",
            commit_message=commit_msg,
            error_message=out or "git commit failed",
        )
        return {"status": "failed", "error": out}

    rev = _run_git(["git", "rev-parse", "HEAD"], cwd=root)
    commit_hash = (rev.stdout or "").strip() if rev.returncode == 0 else None

    push = _run_git(["git", "push", remote, branch], cwd=root)
    push_out = (push.stderr or push.stdout or "").strip()
    if push.returncode != 0:
        crud.add_git_log(
            db,
            plan_date=plan_date,
            status="failed",
            commit_hash=commit_hash,
            commit_message=commit_msg,
            error_message=f"git push failed: {push_out}",
        )
        return {"status": "failed", "error": push_out, "commit_hash": commit_hash}

    crud.add_git_log(
        db,
        plan_date=plan_date,
        status="success",
        commit_hash=commit_hash,
        commit_message=commit_msg,
    )
    return {"status": "success", "commit_hash": commit_hash, "message": commit_msg}
