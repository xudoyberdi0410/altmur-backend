from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base

# from src.auth.models import User
# from src.rooms.models import Room

class Ban(Base):
    __tablename__ = "bans"

    ban_id: Mapped[int] = mapped_column(primary_key=True)
    banned_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    banned_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.room_id"), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    banned_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[banned_user_id],
        back_populates="bans",
    )

    banned_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[banned_by_user_id],
        back_populates="bans_made",
    )
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="ban_list",
    )
    