"""
AI-based job normalization.

Every `RawJob` scraped from any source is passed through an LLM to
extract a consistent, structured shape — regardless of how messy or
differently-formatted the source HTML/text is.
"""
from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup

from app.ai.provider import AIProvider
from app.core.logging import get_logger
from app.scrapers.base import RawJob

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a data extraction engine for job postings. \
Given a raw job posting (title, company, and possibly-messy HTML/text description), \
extract a normalized, structured JSON object.

Respond with ONLY a JSON object matching exactly this schema:
{
  "title": string,
  "company": string,
  "location": string | null,
  "remote": boolean,
  "salary_min": integer | null,
  "salary_max": integer | null,
  "salary_currency": string | null,   // 3-letter code, e.g. "USD"
  "experience_level": string | null,  // one of: intern, junior, mid, senior, staff, principal, lead, manager
  "employment_type": string,          // one of: full_time, part_time, contract, internship, freelance, unknown
  "required_skills": string[],        // concrete technologies/skills, e.g. "Python", "FastAPI", "Docker"
  "responsibilities": string[],       // short bullet-style sentences
  "benefits": string[],               // short bullet-style sentences
  "description": string               // a clean, plain-text 2-4 paragraph summary of the role
}

Rules:
- Infer `remote` from the text (true if fully remote or remote-friendly).
- If salary isn't mentioned, both salary fields must be null.
- Never invent skills or benefits that aren't implied by the text.
- Keep `required_skills` to concrete, specific items (not vague phrases like "good communication").
"""


@dataclass
class NormalizedJob:
    title: str
    company: str
    location: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    experience_level: str | None
    employment_type: str
    required_skills: list[str]
    responsibilities: list[str]
    benefits: list[str]
    description: str


def _strip_html(html: str) -> str:
    if not html:
        return ""
    try:
        return BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()
    except Exception:  # noqa: BLE001
        return html


class JobNormalizer:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def normalize(self, raw_job: RawJob) -> NormalizedJob:
        clean_text = _strip_html(raw_job.raw_description_html)

        user_prompt = (
            f"Title: {raw_job.title}\n"
            f"Company: {raw_job.company}\n"
            f"Location hint: {raw_job.location_text or 'unknown'}\n"
            f"Salary hint: {raw_job.salary_text or 'unknown'}\n"
            f"Employment type hint: {raw_job.employment_type_text or 'unknown'}\n\n"
            f"Description:\n{clean_text[:12000]}"  # defensive truncation for token limits
        )

        try:
            data = await self.ai_provider.extract_json(
                system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt
            )
            return self._to_normalized_job(data, raw_job)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Normalization failed for %s/%s: %s. Falling back to raw fields.",
                raw_job.source, raw_job.source_job_id, exc,
            )
            return self._fallback(raw_job, clean_text)

    def _to_normalized_job(self, data: dict, raw_job: RawJob) -> NormalizedJob:
        return NormalizedJob(
            title=data.get("title") or raw_job.title,
            company=data.get("company") or raw_job.company,
            location=data.get("location"),
            remote=bool(data.get("remote", False)),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            salary_currency=data.get("salary_currency"),
            experience_level=data.get("experience_level"),
            employment_type=data.get("employment_type") or "unknown",
            required_skills=list(data.get("required_skills") or []),
            responsibilities=list(data.get("responsibilities") or []),
            benefits=list(data.get("benefits") or []),
            description=data.get("description") or "",
        )

    def _fallback(self, raw_job: RawJob, clean_text: str) -> NormalizedJob:
        """If the LLM call fails, still persist a usable (if less rich) job record."""
        return NormalizedJob(
            title=raw_job.title,
            company=raw_job.company,
            location=raw_job.location_text,
            remote="remote" in (raw_job.location_text or "").lower(),
            salary_min=None,
            salary_max=None,
            salary_currency=None,
            experience_level=None,
            employment_type="unknown",
            required_skills=[],
            responsibilities=[],
            benefits=[],
            description=clean_text[:2000],
        )
