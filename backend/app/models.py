import uuid
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    wake_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    sleep_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    main_goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    daily_memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_score: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    achievement_rate: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="daily_plan", cascade="all, delete-orphan"
    )
    goal_links: Mapped[list["DailyGoalLink"]] = relationship(
        "DailyGoalLink", back_populates="daily_plan", cascade="all, delete-orphan"
    )


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    daily_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_plans.id", ondelete="CASCADE"), nullable=False
    )
    activity_name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    importance_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    focus_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.utcnow()
    )

    daily_plan: Mapped["DailyPlan"] = relationship("DailyPlan", back_populates="activities")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_goal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True
    )
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    progress: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    daily_links: Mapped[list["DailyGoalLink"]] = relationship(
        "DailyGoalLink", back_populates="goal"
    )


class DailyGoalLink(Base):
    __tablename__ = "daily_goal_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    daily_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_plans.id", ondelete="CASCADE"), nullable=False
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False
    )
    contribution_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    daily_plan: Mapped["DailyPlan"] = relationship("DailyPlan", back_populates="goal_links")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="daily_links")


class GitCommitLog(Base):
    __tablename__ = "git_commit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    commit_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    commit_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.utcnow()
    )
