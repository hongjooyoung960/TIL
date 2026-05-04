from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    activity_name: str
    category: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    duration_minutes: int | None = None
    status: str = "planned"
    importance_score: int = Field(ge=1, le=5, default=3)
    focus_score: int = Field(ge=1, le=5, default=3)
    memo: str | None = None


class ActivityCreate(ActivityBase):
    daily_plan_id: UUID


class ActivityUpdate(BaseModel):
    activity_name: str | None = None
    category: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    duration_minutes: int | None = None
    status: str | None = None
    importance_score: int | None = Field(default=None, ge=1, le=5)
    focus_score: int | None = Field(default=None, ge=1, le=5)
    memo: str | None = None


class ActivityRead(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    daily_plan_id: UUID
    created_at: datetime


class DailyGoalLinkCreate(BaseModel):
    goal_id: UUID
    contribution_score: int = Field(ge=1, le=5, default=3)


class DailyGoalLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    daily_plan_id: UUID
    goal_id: UUID
    contribution_score: int


class DailyPlanBase(BaseModel):
    plan_date: date
    wake_time: time | None = None
    sleep_time: time | None = None
    main_goal: str | None = None
    daily_memo: str | None = None


class DailyPlanCreate(DailyPlanBase):
    goal_links: list[DailyGoalLinkCreate] = []


class DailyPlanUpdate(BaseModel):
    wake_time: time | None = None
    sleep_time: time | None = None
    main_goal: str | None = None
    daily_memo: str | None = None
    goal_links: list[DailyGoalLinkCreate] | None = None


class DailyPlanRead(DailyPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    total_score: float | None = None
    achievement_rate: float | None = None
    created_at: datetime
    updated_at: datetime
    activities: list[ActivityRead] = []
    goal_links: list[DailyGoalLinkRead] = []


class GoalBase(BaseModel):
    title: str
    description: str | None = None
    goal_type: str
    parent_goal_id: UUID | None = None
    target_date: date | None = None
    status: str = "active"
    progress: float = Field(ge=0, le=100, default=0)


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    goal_type: str | None = None
    parent_goal_id: UUID | None = None
    target_date: date | None = None
    status: str | None = None
    progress: float | None = Field(default=None, ge=0, le=100)


class GoalRead(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class WeeklyStatsRead(BaseModel):
    year: int
    week: int
    average_achievement_rate: float | None
    total_focused_time_minutes: float
    total_activity_duration_minutes: float
    category_distribution: dict[str, float]
    average_wake_time: str | None
    average_sleep_time: str | None
    missed_activity_count: int
    achievement_by_day: list[dict[str, Any]]


class GitCommitLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_date: date
    commit_hash: str | None
    commit_message: str | None
    status: str
    error_message: str | None
    created_at: datetime


class ReportFileInfo(BaseModel):
    date: str
    json_path: str
    markdown_path: str | None = None


class DailyAchievementBreakdown(BaseModel):
    basic_achievement_rate: float | None
    weighted_achievement_rate: float | None
    completed_count: int
    missed_count: int
    planned_total: int
