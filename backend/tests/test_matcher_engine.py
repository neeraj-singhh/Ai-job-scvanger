import uuid

import pytest

from app.matcher.engine import (
    build_explanation,
    cosine_similarity,
    hard_filters_pass,
    keyword_overlap_score,
    score_match,
)
from app.models.job import EmploymentType as JobEmploymentType, Job
from app.models.preference import EmploymentType as PrefEmploymentType, Preference


def make_preference(**overrides) -> Preference:
    defaults = dict(
        id=uuid.uuid4(),
        profile_id=uuid.uuid4(),
        preferred_roles=["Backend Engineer"],
        skills=["Python", "FastAPI", "Docker", "PostgreSQL"],
        preferred_locations=["Remote"],
        remote_only=True,
        salary_min=100_000,
        salary_max=None,
        salary_currency="USD",
        experience_level=None,
        company_size=None,
        employment_type=None,
        embedding=None,
    )
    defaults.update(overrides)
    return Preference(**defaults)


def make_job(**overrides) -> Job:
    defaults = dict(
        id=uuid.uuid4(),
        source="remoteok",
        source_job_id="123",
        source_url="https://example.com/job/123",
        title="Senior Backend Engineer",
        company="Acme",
        location="Remote",
        remote=True,
        salary_min=110_000,
        salary_max=150_000,
        salary_currency="USD",
        experience_level="senior",
        employment_type=JobEmploymentType.full_time,
        required_skills=["Python", "FastAPI", "Docker", "Redis"],
        responsibilities=[],
        benefits=[],
        description_raw="raw",
        description_normalized="normalized",
        is_active=True,
        embedding=None,
    )
    defaults.update(overrides)
    return Job(**defaults)


class TestKeywordOverlap:
    def test_full_overlap(self):
        pref = make_preference(skills=["Python", "Docker"])
        job = make_job(required_skills=["Python", "Docker"])
        score, matched, missing = keyword_overlap_score(pref, job)
        assert score == 1.0
        assert matched == ["docker", "python"]
        assert missing == []

    def test_partial_overlap(self):
        pref = make_preference(skills=["Python", "Docker"])
        job = make_job(required_skills=["Python", "Redis"])
        score, matched, missing = keyword_overlap_score(pref, job)
        assert score == 0.5
        assert matched == ["python"]
        assert missing == ["redis"]

    def test_no_preference_skills_returns_zero(self):
        pref = make_preference(skills=[])
        job = make_job(required_skills=["Python"])
        score, matched, missing = keyword_overlap_score(pref, job)
        assert score == 0.0
        assert matched == []


class TestCosineSimilarity:
    def test_identical_vectors(self):
        assert cosine_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)

    def test_zero_vector_returns_zero(self):
        assert cosine_similarity([0, 0], [1, 1]) == 0.0


class TestHardFilters:
    def test_remote_only_rejects_onsite_job(self):
        pref = make_preference(remote_only=True)
        job = make_job(remote=False)
        assert hard_filters_pass(pref, job) is False

    def test_location_mismatch_rejects_job(self):
        pref = make_preference(remote_only=False, preferred_locations=["Berlin"])
        job = make_job(remote=False, location="New York")
        assert hard_filters_pass(pref, job) is False

    def test_salary_below_minimum_rejects_job(self):
        pref = make_preference(salary_min=200_000, remote_only=False, preferred_locations=[])
        job = make_job(salary_max=150_000)
        assert hard_filters_pass(pref, job) is False

    def test_employment_type_mismatch_rejects_job(self):
        pref = make_preference(
            employment_type=PrefEmploymentType.contract, remote_only=False, preferred_locations=[]
        )
        job = make_job(employment_type=JobEmploymentType.full_time)
        assert hard_filters_pass(pref, job) is False

    def test_matching_job_passes(self):
        pref = make_preference()
        job = make_job()
        assert hard_filters_pass(pref, job) is True


class TestScoreMatch:
    def test_filtered_job_returns_none(self):
        pref = make_preference(remote_only=True)
        job = make_job(remote=False)
        assert score_match(pref, job) is None

    def test_scored_job_blends_keyword_and_semantic(self):
        pref = make_preference(skills=["Python", "FastAPI"], embedding=[1.0, 0.0])
        job = make_job(required_skills=["Python", "FastAPI"], embedding=[1.0, 0.0])
        result = score_match(pref, job)
        assert result is not None
        assert result.score == pytest.approx(1.0, abs=0.01)
        assert "python" in result.matched_skills

    def test_explanation_format(self):
        text = build_explanation(["python", "docker"], ["redis"], 0.82)
        assert "82%" in text
        assert "\u2713 python" in text
        assert "redis" in text
