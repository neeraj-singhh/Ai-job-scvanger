import uuid

from pydantic import BaseModel, Field, model_validator

from app.models.preference import CompanySize, EmploymentType, ExperienceLevel


class PreferenceBase(BaseModel):
    preferred_roles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_only: bool = False
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str = Field(default="USD", min_length=3, max_length=3)
    experience_level: ExperienceLevel | None = None
    company_size: CompanySize | None = None
    employment_type: EmploymentType | None = None

    @model_validator(mode="after")
    def validate_salary_range(self) -> "PreferenceBase":
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_min > self.salary_max:
                raise ValueError("salary_min cannot be greater than salary_max")
        return self


class PreferenceUpdate(PreferenceBase):
    pass


class PreferenceResponse(PreferenceBase):
    id: uuid.UUID
    profile_id: uuid.UUID

    model_config = {"from_attributes": True}
