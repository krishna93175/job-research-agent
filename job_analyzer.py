import json

from agents import Agent, Runner
from dotenv import load_dotenv

from models import JobAnalysis


load_dotenv()


analyzer_agent = Agent(
    name="Job Posting Analyzer",

    instructions="""
Analyze a job posting and convert it into structured information.

Return ONLY valid JSON using exactly this structure:

{
    "role_relevance": "strong | moderate | weak | irrelevant",

    "required_experience_min": null,
    "required_experience_max": null,

    "required_skills": [],

    "employment_type": null,

    "remote_status": null,
    "remote_scope": null,

    "location_requirements": null,

    "visa_sponsorship": "confirmed | not_confirmed | unavailable",

    "international_eligibility": "confirmed | unclear | restricted | unavailable",

    "evidence": [],

    "concerns": []
}

Rules:

- Analyze only information present in the supplied job posting.
- Do not invent requirements.
- Do not assume that remote means worldwide remote.
- Do not assume that a company accepts international applicants.
- Do not assume visa sponsorship unless the posting provides evidence.
- Distinguish between information that is confirmed and information that
  is simply not stated.
- Extract minimum and maximum experience requirements when explicitly
  stated.
- Identify important required skills.
- Identify employment type when available.
- Identify geographic restrictions when available.
- Evidence should contain short factual statements supporting your analysis.
- Concerns should identify important uncertainties or potential problems.
- If information is unavailable, use null or the appropriate
  "unavailable"/"unclear" value.
""",
)


def analyze_job(job) -> JobAnalysis:
    """
    Analyze one job posting using the AI model.
    """

    # Limit description size to prevent unnecessarily large requests.
    description = job.description[:12000]

    prompt = f"""
Analyze this job posting.

TITLE:
{job.title}

COMPANY:
{job.company}

LOCATION:
{job.location}

REMOTE:
{job.remote}

TAGS:
{", ".join(job.tags)}

JOB TYPES:
{", ".join(job.job_types)}

DESCRIPTION:
{description}

SOURCE:
{job.url}
"""

    result = Runner.run_sync(
        analyzer_agent,
        prompt,
    )

    parsed = json.loads(result.final_output)

    return JobAnalysis(
        role_relevance=parsed.get(
            "role_relevance",
            "unknown",
        ),
        required_experience_min=parsed.get(
            "required_experience_min"
        ),
        required_experience_max=parsed.get(
            "required_experience_max"
        ),
        required_skills=parsed.get(
            "required_skills",
            [],
        ),
        employment_type=parsed.get(
            "employment_type"
        ),
        remote_status=parsed.get(
            "remote_status"
        ),
        remote_scope=parsed.get(
            "remote_scope"
        ),
        location_requirements=parsed.get(
            "location_requirements"
        ),
        visa_sponsorship=parsed.get(
            "visa_sponsorship",
            "unavailable",
        ),
        international_eligibility=parsed.get(
            "international_eligibility",
            "unavailable",
        ),
        evidence=parsed.get(
            "evidence",
            [],
        ),
        concerns=parsed.get(
            "concerns",
            [],
        ),
    )