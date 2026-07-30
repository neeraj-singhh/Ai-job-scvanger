"""
Profile model.

Supabase Auth owns the `auth.users` table (email, password hash, etc).
This `profiles` table is our app-side extension of that identity,
keyed by the same UUID that Supabase Auth issues (auth.users.id).
"""
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    # Same UUID as Supabase auth.users.id (no FK across schemas in app code;
    # enforced via DB trigger / Supabase's auth schema in supabase/schema.sql)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    preferences: Mapped["Preference"] = relationship(
        back_populates="profile", uselist=False, cascade="all, delete-orphan"
    )
    saved_jobs: Mapped[list["SavedJob"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    matches: Mapped[list["JobMatch"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    resume_uploads: Mapped[list["ResumeUpload"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["NotificationHistory"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
