from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base

# from src.auth.models import User
# from src.rooms.models import Room

class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"), nullable=False, index=True)
    reply_to: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.message_id"), nullable=True)
    message: Mapped[str] = mapped_column(String(4096), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="messages")
    room: Mapped["Room"] = relationship("Room", back_populates="messages")
    parent: Mapped[Optional["Message"]] = relationship("Message", back_populates="replies", remote_side="Message.message_id")
    replies: Mapped[List["Message"]] = relationship("Message", back_populates="parent")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    pinned_messages: Mapped[List["PinnedMessage"]] = relationship("PinnedMessage", back_populates="message", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = "attachments"

    attachment_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.message_id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    message: Mapped["Message"] = relationship("Message", back_populates="attachments")


class PinnedMessage(Base):
    __tablename__ = "pinned_messages"

    pin_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.message_id"), nullable=False, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"), nullable=False, index=True)
    pinned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    message: Mapped["Message"] = relationship("Message", back_populates="pinned_messages")
    room: Mapped["Room"] = relationship("Room", back_populates="pinned_messages")