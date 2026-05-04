import json
from pathlib import Path

from fastapi import APIRouter

from ..services.report_service import project_root

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/list")
def list_reports():
    root = project_root()
    daily_dir = root / "daily"
    reports_dir = root / "reports"
    daily_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    dates: dict[str, dict[str, str]] = {}
    for p in sorted(daily_dir.glob("*.json")):
        stem = p.stem
        dates.setdefault(stem, {})["json_path"] = str(p.relative_to(root))
        dates[stem]["date"] = stem
    for p in sorted(reports_dir.glob("*-report.md")):
        stem = p.name.replace("-report.md", "")
        dates.setdefault(stem, {})["markdown_path"] = str(p.relative_to(root))
        dates[stem]["date"] = stem

    summaries = []
    for ds in sorted(dates.keys(), reverse=True):
        info = dates[ds]
        preview = {}
        jp = root / "daily" / f"{ds}.json"
        if jp.exists():
            try:
                preview = json.loads(jp.read_text(encoding="utf-8"))
            except Exception:
                preview = {}
        summaries.append(
            {
                "date": ds,
                "json_path": info.get("json_path"),
                "markdown_path": info.get("markdown_path"),
                "achievement_rate_weighted": preview.get("achievement_rate_weighted"),
                "main_goal": preview.get("main_goal"),
            }
        )
    return summaries
