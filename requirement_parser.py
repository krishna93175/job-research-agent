import json

from agents import Agent, Runner
from dotenv import load_dotenv

from models import (
    JobRequirements,
    CandidateProfile,
)

from llm_client import generate_json


load_dotenv()


PARSER_INSTRUCTIONS = """
Convert a user's job-search request into two structured
objects:

1. JobRequirements
2. CandidateProfile

Return ONLY valid JSON using exactly this structure:

{
    "job_requirements": {
        "role": null,
        "location": null,
        "remote_required": false,
        "hybrid_allowed": true,
        "min_experience_years": null,
        "max_experience_years": null,
        "employment_types": [],
        "skills": [],
        "salary_min": null,
        "salary_max": null,
        "salary_currency": null,
        "applicant_country": null,
        "visa_required": false,
        "keywords": []
    },

    "candidate_profile": {
        "experience_years": null,
        "skills": [],
        "education": [],
        "current_country": null,
        "desired_locations": [],
        "desired_employment_types": []
    }
}

Rules:

- Information about the JOB goes into job_requirements.
- Information about the USER/CANDIDATE goes into candidate_profile.
- Do not confuse candidate experience with required job experience.
- If the user says "I have 1 year of experience",
  candidate_profile.experience_years = 1.
- If the user says "the job requires 1 year",
  job_requirements.min_experience_years = 1.
- If the user says "I want a job requiring 2-5 years",
  use min_experience_years = 2 and
  max_experience_years = 5.
- Do not invent missing information.
- Use null for unknown scalar values.
- Use [] for unknown lists.
"""


def parse_requirements(
    user_request: str,
) -> tuple[
    JobRequirements,
    CandidateProfile,
]:

    parsed = generate_json(
        system_prompt=PARSER_INSTRUCTIONS,
        user_prompt=user_request,
    )

    job_data = parsed[
        "job_requirements"
    ]

    candidate_data = parsed[
        "candidate_profile"
    ]

    job_requirements = JobRequirements(
        role=job_data.get(
            "role"
        ),

        location=job_data.get(
            "location"
        ),

        remote_required=job_data.get(
            "remote_required",
            False,
        ),

        hybrid_allowed=job_data.get(
            "hybrid_allowed",
            True,
        ),

        min_experience_years=job_data.get(
            "min_experience_years"
        ),

        max_experience_years=job_data.get(
            "max_experience_years"
        ),

        employment_types=job_data.get(
            "employment_types",
            [],
        ),

        skills=job_data.get(
            "skills",
            [],
        ),

        salary_min=job_data.get(
            "salary_min"
        ),

        salary_max=job_data.get(
            "salary_max"
        ),

        salary_currency=job_data.get(
            "salary_currency"
        ),

        applicant_country=job_data.get(
            "applicant_country"
        ),

        visa_required=job_data.get(
            "visa_required",
            False,
        ),

        keywords=job_data.get(
            "keywords",
            [],
        ),
    )

    candidate_profile = CandidateProfile(
        experience_years=candidate_data.get(
            "experience_years"
        ),

        skills=candidate_data.get(
            "skills",
            [],
        ),

        education=candidate_data.get(
            "education",
            [],
        ),

        current_country=candidate_data.get(
            "current_country"
        ),

        desired_locations=candidate_data.get(
            "desired_locations",
            [],
        ),

        desired_employment_types=(
            candidate_data.get(
                "desired_employment_types",
                [],
            )
        ),
    )

    return (
        job_requirements,
        candidate_profile,
    )