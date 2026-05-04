"""Initial schema.

Revision ID: 001_initial
Revises:
Create Date: 2026-05-04
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("wake_time", sa.Time(), nullable=True),
        sa.Column("sleep_time", sa.Time(), nullable=True),
        sa.Column("main_goal", sa.Text(), nullable=True),
        sa.Column("daily_memo", sa.Text(), nullable=True),
        sa.Column("total_score", sa.Numeric(10, 4), nullable=True),
        sa.Column("achievement_rate", sa.Numeric(10, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("uq_daily_plans_plan_date", "daily_plans", ["plan_date"], unique=True)

    op.create_table(
        "goals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("goal_type", sa.String(length=32), nullable=False),
        sa.Column("parent_goal_id", UUID(as_uuid=True), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("progress", sa.Numeric(10, 4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_goal_id"], ["goals.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "activities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("daily_plan_id", UUID(as_uuid=True), nullable=False),
        sa.Column("activity_name", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("importance_score", sa.Integer(), nullable=False),
        sa.Column("focus_score", sa.Integer(), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["daily_plan_id"], ["daily_plans.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "daily_goal_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("daily_plan_id", UUID(as_uuid=True), nullable=False),
        sa.Column("goal_id", UUID(as_uuid=True), nullable=False),
        sa.Column("contribution_score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["daily_plan_id"], ["daily_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "git_commit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("commit_hash", sa.Text(), nullable=True),
        sa.Column("commit_message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("git_commit_logs")
    op.drop_table("daily_goal_links")
    op.drop_table("activities")
    op.drop_table("goals")
    op.drop_table("daily_plans")
