from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_dep
from app.models.job import EmploymentType
from app.schemas.auth import AuthUser
from app.schemas.job import (
    JobListParams,
    JobMatchResponse,
    JobResponse,
    SavedJobRequest,
    SavedJobResponse,
)
from app.services.job_service import JobService

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    query: str | None = None,
    location: str | None = None,
    remote_only: bool = False,
    employment_type: EmploymentType | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> list[JobResponse]:
    params = JobListParams(
        query=query,
        location=location,
        remote_only=remote_only,
        employment_type=employment_type,
        page=page,
        page_size=page_size,
    )
    jobs, _total = await JobService(db).list_jobs(params)
    return jobs


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str, current_user: AuthUser = Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)
) -> JobResponse:
    import uuid

    return await JobService(db).get_job(uuid.UUID(job_id))


@router.get("/matches", response_model=list[JobMatchResponse])
async def get_matches(
    min_score: float = Query(default=0.0, ge=0.0, le=1.0),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> list[JobMatchResponse]:
    return await JobService(db).get_matches_for_profile(current_user.id, min_score=min_score)


@router.post("/saved", response_model=SavedJobResponse, status_code=201)
async def save_job(
    payload: SavedJobRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> SavedJobResponse:
    return await JobService(db).save_job(current_user.id, payload)


@router.get("/saved", response_model=list[SavedJobResponse])
async def list_saved_jobs(
    current_user: AuthUser = Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)
) -> list[SavedJobResponse]:
    return await JobService(db).list_saved_jobs(current_user.id)


@router.delete("/saved/{job_id}", status_code=204)
async def delete_saved_job(
    job_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_dep),
) -> None:
    import uuid

    await JobService(db).delete_saved_job(current_user.id, uuid.UUID(job_id))
