"""pairing codes + device tokens

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-27

"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pairing_codes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=12), nullable=False),
        sa.Column("consumed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pairing_codes_user_id", "pairing_codes", ["user_id"], unique=False)
    op.create_index("ix_pairing_codes_code", "pairing_codes", ["code"], unique=True)

    op.create_table(
        "device_tokens",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_device_tokens_device_id", "device_tokens", ["device_id"], unique=False)
    op.create_index("ix_device_tokens_token_hash", "device_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_device_tokens_token_hash", table_name="device_tokens")
    op.drop_index("ix_device_tokens_device_id", table_name="device_tokens")
    op.drop_table("device_tokens")

    op.drop_index("ix_pairing_codes_code", table_name="pairing_codes")
    op.drop_index("ix_pairing_codes_user_id", table_name="pairing_codes")
    op.drop_table("pairing_codes")
