"""device logs

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-27

"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False, server_default=sa.text("'info'")),
        sa.Column("message", sa.String(length=4000), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_device_logs_device_id", "device_logs", ["device_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_device_logs_device_id", table_name="device_logs")
    op.drop_table("device_logs")
