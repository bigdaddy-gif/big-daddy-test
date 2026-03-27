from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False)  # windows|macos
    status: Mapped[str] = mapped_column(String(32), default="offline", nullable=False)
    last_seen_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
