import requirement_parser


MOCK_LLM_RESPONSE = {
    "job_requirements": {
        "role": "Data Analyst",
        "location": "India",
        "remote_required": True,
        "hybrid_allowed": True,
        "min_experience_years": 0,
        "max_experience_years": 2,
        "employment_types": ["Full-time"],
        "skills": ["Excel", "SQL"],
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "applicant_country": "India",
        "visa_required": False,
        "keywords": [
            "remote",
            "junior",
            "data analyst",
            "India",
        ],
    },
    "candidate_profile": {
        "experience_years": 1,
        "skills": ["Excel", "SQL"],
        "education": [],
        "current_country": "India",
        "desired_locations": ["India"],
        "desired_employment_types": ["Full-time"],
    },
}


def mock_generate_json(
    system_prompt: str,
    user_prompt: str,
) -> dict:
    """
    Return a deterministic LLM response for testing.

    This prevents the test from requiring Groq/OpenAI
    credentials or network access.
    """

    assert system_prompt == requirement_parser.PARSER_INSTRUCTIONS
    assert "data analyst" in user_prompt.lower()

    return MOCK_LLM_RESPONSE


# Replace the real LLM call with the deterministic mock.
requirement_parser.generate_json = mock_generate_json


request = """
Find remote junior data analyst jobs in India.
I have about 1 year of experience and know Excel and
SQL.
I prefer full-time positions.
"""


job_requirements, candidate_profile = (
    requirement_parser.parse_requirements(
        request
    )
)


print()
print("JOB REQUIREMENTS")
print(job_requirements)

print()
print("CANDIDATE PROFILE")
print(candidate_profile)


# -------------------------------------------------
# Assertions
# -------------------------------------------------

assert job_requirements.role == "Data Analyst"
assert job_requirements.location == "India"
assert job_requirements.remote_required is True
assert job_requirements.hybrid_allowed is True

assert job_requirements.min_experience_years == 0
assert job_requirements.max_experience_years == 2

assert job_requirements.employment_types == [
    "Full-time"
]

assert job_requirements.skills == [
    "Excel",
    "SQL",
]

assert job_requirements.applicant_country == "India"
assert job_requirements.visa_required is False

assert "remote" in [
    keyword.lower()
    for keyword in job_requirements.keywords
]

assert candidate_profile.experience_years == 1

assert candidate_profile.skills == [
    "Excel",
    "SQL",
]

assert candidate_profile.current_country == "India"

assert candidate_profile.desired_locations == [
    "India"
]

assert candidate_profile.desired_employment_types == [
    "Full-time"
]


print()
print("REQUIREMENT PARSER TEST: PASSED")