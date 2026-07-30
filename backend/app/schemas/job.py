import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.job import EmploymentType


class JobResponse(BaseModel):
    id: uuid.UUID
    source: str
    source_url: str
    title: str
    company: str
    location: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    experience_level: str | None
    employment_type: EmploymentType
    required_skills: list[str]
    responsibilities: list[str]
    benefits: list[str]
    description_normalized: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListParams(BaseModel):
    query: str | None = None
    location: str | None = None
    remote_only: bool = False
    employment_type: EmploymentType | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class JobMatchResponse(BaseModel):
    id: uuid.UUID
    job: JobResponse
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
    notified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SavedJobRequest(BaseModel):
    job_id: uuid.UUID
    notes: str | None = None


class SavedJobResponse(BaseModel):
    id: uuid.UUID
    job: JobResponse
    notes: str | None
    applied: bool
    created_at: datetime

    model_config = {"from_attributes": True}
