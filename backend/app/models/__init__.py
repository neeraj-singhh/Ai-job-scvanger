"""
Import every model here so SQLAlchemy's declarative registry can resolve
string-based relationship() references (e.g. "Profile", "Job") regardless
of which module is imported first.
"""
from app.models.profile import Profile  # noqa: F401
from app.models.preference import Preference, ExperienceLevel, CompanySize, EmploymentType  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.matching import (  # noqa: F401
    JobMatch,
    SavedJob,
    NotificationHistory,
    NotificationType,
    ResumeUpload,
)

__all__ = [
    "Profile",
    "Preference",
    "ExperienceLevel",
    "CompanySize",
    "EmploymentType",
    "Job",
    "JobMatch",
    "SavedJob",
    "NotificationHistory",
    "NotificationType",
    "ResumeUpload",
]
