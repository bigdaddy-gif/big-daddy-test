"""init

Revision ID: 0001
Revises: 
Create Date: 2026-03-27

"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "entitlements",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sku", sa.String(length=64), nullable=False, server_default=sa.text("setup_1000")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_entitlements_user_id", "entitlements", ["user_id"], unique=False)

    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("offline")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_devices_user_id", "devices", ["user_id"], unique=False)

    op.create_table(
        "magic_link_tokens",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("consumed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_magic_email", "magic_link_tokens", ["email"], unique=False)
    op.create_index("ix_magic_token_hash", "magic_link_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_magic_token_hash", table_name="magic_link_tokens")
    op.drop_index("ix_magic_email", table_name="magic_link_tokens")
    op.drop_table("magic_link_tokens")

    op.drop_index("ix_devices_user_id", table_name="devices")
    op.drop_table("devices")

    op.drop_index("ix_entitlements_user_id", table_name="entitlements")
    op.drop_table("entitlements")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
