import enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Boolean, Enum, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

# Must match the dimensionality of AI_PROVIDER's embedding model
# (1536 for OpenAI text-embedding-3-small).
EMBEDDING_DIM = 1536


class EmploymentType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"
    freelance = "freelance"
    unknown = "unknown"


class Job(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    """
    Canonical, AI-normalized job record. Every scraper produces a raw
    `RawJob` (see scrapers/base.py) which is normalized into this shape
    before being persisted here.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        # A job is uniquely identified by which provider it came from
        # plus that provider's native id/url, preventing duplicate ingestion.
        UniqueConstraint("source", "source_job_id", name="uq_jobs_source_source_job_id"),
        Index("ix_jobs_title_company", "title", "company"),
    )

    source: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "greenhouse", "remoteok"
    source_job_id: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2000), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    company: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False)

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)

    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType, name="job_employment_type"), default=EmploymentType.unknown
    )

    required_skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    responsibilities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    benefits: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    description_raw: Mapped[str] = mapped_column(Text, nullable=False)
    description_normalized: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # false once delisted

    # pgvector column for semantic similarity search (Stage 2 matching).
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    matches: Mapped[list["JobMatch"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    saved_by: Mapped[list["SavedJob"]] = relationship(back_populates="job", cascade="all, delete-orphan")
