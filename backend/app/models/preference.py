import enum
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

# Must match app/models/job.py's EMBEDDING_DIM and the configured AI
# provider's embedding model dimensionality (1536 for OpenAI
# text-embedding-3-small).
EMBEDDING_DIM = 1536


class ExperienceLevel(str, enum.Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    staff = "staff"
    principal = "principal"
    lead = "lead"
    manager = "manager"


class CompanySize(str, enum.Enum):
    startup = "startup"          # 1-50
    small = "small"               # 51-200
    medium = "medium"             # 201-1000
    large = "large"               # 1001-5000
    enterprise = "enterprise"     # 5000+


class EmploymentType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"
    freelance = "freelance"


class Preference(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "preferences"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    preferred_roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    preferred_locations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    remote_only: Mapped[bool] = mapped_column(Boolean, default=False)

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")

    experience_level: Mapped[ExperienceLevel | None] = mapped_column(
        Enum(ExperienceLevel, name="experience_level"), nullable=True
    )
    company_size: Mapped[CompanySize | None] = mapped_column(
        Enum(CompanySize, name="company_size"), nullable=True
    )
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(EmploymentType, name="employment_type"), nullable=True
    )

    # Cached embedding of the preference profile (role + skills + free text)
    # so matching doesn't need to re-embed on every scheduler run.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="preferences")
