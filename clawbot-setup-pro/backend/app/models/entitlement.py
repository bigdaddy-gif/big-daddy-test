from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Entitlement(Base):
    __tablename__ = "entitlements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(64), default="setup_1000", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
