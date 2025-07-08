from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column,  relationship
from sqlalchemy.sql import func

from src.core.database import Base
from src.auth.models import User
from src.chat.models import Message, PinnedMessage
from src.moderation.models import BanList


class RoomRole(str, PyEnum):
    owner = "owner"
    moderator = "moderator"
    member = "member"

class Room(Base):
    __tablename__ = "rooms"

    room_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_private: Mapped[bool] = mapped_column(default=True)
    description: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    pinned_messages: Mapped[List["PinnedMessage"]] = relationship(
        "PinnedMessage",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    join_links: Mapped[List["JoinLink"]] = relationship(
        "JoinLink",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    room_members: Mapped[List["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    ban_list: Mapped[List["BanList"]] = relationship(
        "BanList",
        back_populates="room",
        cascade="all, delete-orphan",
    )


class RoomMember(Base):
    __tablename__ = "room_members"

    member_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"), nullable=False)
    role: Mapped[RoomRole] = mapped_column(Enum(RoomRole, name="room_role"), default=RoomRole.member, nullable=False)
    joined_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    link_id: Mapped[Optional[int]] = mapped_column(ForeignKey("join_links.link_id"), nullable=True)
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="room_members"
    )
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="room_members"
    )
    link: Mapped[Optional["JoinLink"]] = relationship(
        "JoinLink",
        back_populates="room_members",
        uselist=False
    )
class JoinLink(Base):
    __tablename__ = "join_links"

    link_id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False) # Link creator
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    expired_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)

    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="join_links"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="join_links"
    )
    room_members: Mapped[List["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="link",
    )