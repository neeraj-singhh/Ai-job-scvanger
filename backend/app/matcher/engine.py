"""
Two-stage job matching engine.

Stage 1 (cheap, fast): keyword overlap filtering to discard obviously
irrelevant jobs before spending AI calls on them.

Stage 2 (semantic): cosine similarity between the user's preference
embedding and the job's embedding, blended with the keyword score to
produce a final 0-1 match score plus a human-readable explanation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.job import Job
from app.models.preference import Preference

# Weighting between keyword overlap and semantic similarity in the final score.
KEYWORD_WEIGHT = 0.35
SEMANTIC_WEIGHT = 0.65

# Stage 1 gate: jobs below this raw keyword overlap ratio are discarded
# before semantic scoring even runs (saves embedding compute on junk).
MIN_KEYWORD_OVERLAP_TO_CONSIDER = 0.0  # 0 = don't gate on keywords alone; role terms still help ranking


@dataclass
class MatchResult:
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


def _normalize_terms(terms: list[str]) -> set[str]:
    return {t.strip().lower() for t in terms if t and t.strip()}


def keyword_overlap_score(preference: Preference, job: Job) -> tuple[float, list[str], list[str]]:
    """Stage 1: simple keyword/skill overlap between preferences and the job."""
    pref_skills = _normalize_terms(preference.skills)
    job_skills = _normalize_terms(job.required_skills)

    if not pref_skills:
        return 0.0, [], list(job.required_skills)

    matched = pref_skills & job_skills
    missing = job_skills - pref_skills

    score = len(matched) / max(len(pref_skills), 1)
    return min(score, 1.0), sorted(matched), sorted(missing)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a, b = np.array(vec_a), np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def hard_filters_pass(preference: Preference, job: Job) -> bool:
    """Non-negotiable filters applied before scoring at all."""
    if preference.remote_only and not job.remote:
        return False

    if preference.preferred_locations and not job.remote:
        job_location = (job.location or "").lower()
        if not any(loc.lower() in job_location for loc in preference.preferred_locations):
            return False

    if preference.salary_min and job.salary_max:
        if job.salary_max < preference.salary_min:
            return False

    if preference.employment_type and job.employment_type != preference.employment_type:
        return False

    return True


def build_explanation(matched: list[str], missing: list[str], score: float) -> str:
    lines = [f"Matched because ({round(score * 100)}% match):"]
    for skill in matched[:8]:
        lines.append(f"\u2713 {skill}")
    if missing:
        lines.append("Missing:")
        for skill in missing[:5]:
            lines.append(skill)
    return "\n".join(lines)


def score_match(preference: Preference, job: Job) -> MatchResult | None:
    """
    Returns None if the job fails hard filters (should not be persisted as a match).
    Otherwise returns a MatchResult with a blended 0-1 score.
    """
    if not hard_filters_pass(preference, job):
        return None

    kw_score, matched_skills, missing_skills = keyword_overlap_score(preference, job)

    semantic_score = 0.0
    if preference.embedding and job.embedding:
        semantic_score = max(cosine_similarity(preference.embedding, job.embedding), 0.0)

    final_score = (KEYWORD_WEIGHT * kw_score) + (SEMANTIC_WEIGHT * semantic_score)
    final_score = round(min(final_score, 1.0), 4)

    explanation = build_explanation(matched_skills, missing_skills, final_score)

    return MatchResult(
        score=final_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        explanation=explanation,
    )
