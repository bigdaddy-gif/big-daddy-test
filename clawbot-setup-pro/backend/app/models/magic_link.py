from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MagicLinkToken(Base):
    __tablename__ = "magic_link_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
