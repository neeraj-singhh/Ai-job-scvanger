import enum
import uuid

from sqlalchemy import ARRAY, Boolean, Enum, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class JobMatch(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """A scored match between a user's preferences and a job."""

    __tablename__ = "job_matches"
    __table_args__ = (
        UniqueConstraint("profile_id", "job_id", name="uq_job_matches_profile_job"),
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 1.0
    matched_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    missing_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    notified: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["Profile"] = relationship(back_populates="matches")
    job: Mapped["Job"] = relationship(back_populates="matches")


class SavedJob(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "saved_jobs"
    __table_args__ = (
        UniqueConstraint("profile_id", "job_id", name="uq_saved_jobs_profile_job"),
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["Profile"] = relationship(back_populates="saved_jobs")
    job: Mapped["Job"] = relationship(back_populates="saved_by")


class NotificationType(str, enum.Enum):
    new_match = "new_match"
    system = "system"


class NotificationHistory(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "notification_history"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_match_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_matches.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"), default=NotificationType.new_match
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["Profile"] = relationship(back_populates="notifications")


class ResumeUpload(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "resume_uploads"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    parsed_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    parsed_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["Profile"] = relationship(back_populates="resume_uploads")
