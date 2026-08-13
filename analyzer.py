import json
from dataclasses import dataclass, field

from models import Job
from llm_client import generate_json


@dataclass
class JobAnalysis:
    role_relevance: str

    required_experience_min: int | None
    required_experience_max: int | None

    required_skills: list[str] = field(
        default_factory=list
    )

    preferred_skills: list[str] = field(
        default_factory=list
    )

    employment_type: str | None = None

    remote_status: str = "unclear"
    remote_scope: str | None = None

    international_eligibility: str = "unclear"
    visa_sponsorship: str = "not_confirmed"

    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None

    evidence: list[str] = field(
        default_factory=list
    )

    concerns: list[str] = field(
        default_factory=list
    )


ANALYZER_INSTRUCTIONS = """
You are a job listing analysis agent.

Analyze the supplied job listing and extract only information
supported by the listing.

Do not invent missing information.

Important rules:

1. Distinguish between required and preferred qualifications.

2. If experience is not stated, return null.

3. If salary is not stated, return null.

4. If visa sponsorship is not mentioned, return
   "not_confirmed".

5. If international applicant eligibility is not stated,
   return "unclear".

6. Remote status must distinguish between:
   - remote
   - hybrid
   - onsite
   - unclear

7. Evidence must contain concise facts directly supported
   by the listing.

8. Concerns should identify important missing or ambiguous
   information.

9. Evaluate role relevance based on the requested role
   and the actual job listing.

10. Return valid JSON only.

Required JSON structure:

{
    "role_relevance": "strong | moderate | weak | unclear",

    "required_experience_min": null,
    "required_experience_max": null,

    "required_skills": [],
    "preferred_skills": [],

    "employment_type": null,

    "remote_status": "remote | hybrid | onsite | unclear",
    "remote_scope": null,

    "international_eligibility": "yes | no | unclear",
    "visa_sponsorship": "confirmed | not_confirmed | no",

    "salary_min": null,
    "salary_max": null,
    "salary_currency": null,

    "evidence": [],
    "concerns": []
}
"""


def build_analysis_prompt(
    job: Job,
    requested_role: str | None = None,
) -> str:
    """
    Build the prompt sent to the analyzer.
    """

    requested_role_text = (
        requested_role
        if requested_role
        else "Not specified"
    )

    return f"""
Analyze this job listing.

REQUESTED ROLE:
{requested_role_text}

JOB TITLE:
{job.title}

COMPANY:
{job.company}

LOCATION:
{job.location}

REMOTE:
{job.remote}

REMOTE SCOPE:
{job.remote_scope}

EMPLOYMENT TYPES:
{job.job_types}

TAGS:
{job.tags}

DESCRIPTION:
{job.description}

SOURCE:
{job.source}

SOURCE URL:
{job.url}

Return only the required JSON object.
"""


def parse_analysis(
    response_data: dict,
) -> JobAnalysis:
    """
    Convert analyzer JSON into a JobAnalysis object.
    """

    return JobAnalysis(
        role_relevance=response_data.get(
            "role_relevance",
            "unclear",
        ),

        required_experience_min=response_data.get(
            "required_experience_min"
        ),

        required_experience_max=response_data.get(
            "required_experience_max"
        ),

        required_skills=response_data.get(
            "required_skills",
            [],
        ),

        preferred_skills=response_data.get(
            "preferred_skills",
            [],
        ),

        employment_type=response_data.get(
            "employment_type"
        ),

        remote_status=response_data.get(
            "remote_status",
            "unclear",
        ),

        remote_scope=response_data.get(
            "remote_scope"
        ),

        international_eligibility=response_data.get(
            "international_eligibility",
            "unclear",
        ),

        visa_sponsorship=response_data.get(
            "visa_sponsorship",
            "not_confirmed",
        ),

        salary_min=response_data.get(
            "salary_min"
        ),

        salary_max=response_data.get(
            "salary_max"
        ),

        salary_currency=response_data.get(
            "salary_currency"
        ),

        evidence=response_data.get(
            "evidence",
            [],
        ),

        concerns=response_data.get(
            "concerns",
            [],
        ),
    )


def analyze_job(
    job: Job,
    requested_role: str | None = None,
) -> JobAnalysis:
    """
    Analyze one job listing.

    Uses Groq GPT-OSS 120B as the primary model
    through the shared LLM provider layer.
    """

    prompt = build_analysis_prompt(
        job,
        requested_role,
    )

    result = generate_json(
        system_prompt=ANALYZER_INSTRUCTIONS,
        user_prompt=prompt,
        groq_model="openai/gpt-oss-120b",
    )

    return parse_analysis(
        result
    )