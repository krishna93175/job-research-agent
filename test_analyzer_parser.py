from analyzer import parse_analysis


fake_response = """
{
    "role_relevance": "strong",
    "required_experience_min": 0,
    "required_experience_max": 2,
    "required_skills": [
        "Excel",
        "SQL",
        "analytical and communication skills"
    ],
    "preferred_skills": [
        "Power BI"
    ],
    "employment_type": "full-time",
    "remote_status": "remote",
    "remote_scope": "fully remote",
    "international_eligibility": "unclear",
    "visa_sponsorship": "not_confirmed",
    "salary_min": null,
    "salary_max": null,
    "salary_currency": null,
    "evidence": [
        "The listing states 0–2 years of experience.",
        "Excel and SQL are listed as requirements.",
        "Power BI is listed as preferred.",
        "The listing states that the position is full-time and remote."
    ],
    "concerns": [
        "International applicant eligibility is not stated.",
        "Visa sponsorship is not confirmed.",
        "Salary information is not provided."
    ]
}
"""


analysis = parse_analysis(
    fake_response
)


print("ANALYSIS")
print("=" * 60)

print(
    "Role relevance:",
    analysis.role_relevance,
)

print(
    "Experience:",
    analysis.required_experience_min,
    "-",
    analysis.required_experience_max,
)

print(
    "Required skills:",
    analysis.required_skills,
)

print(
    "Preferred skills:",
    analysis.preferred_skills,
)

print(
    "Employment:",
    analysis.employment_type,
)

print(
    "Remote:",
    analysis.remote_status,
)

print(
    "International eligibility:",
    analysis.international_eligibility,
)

print(
    "Visa sponsorship:",
    analysis.visa_sponsorship,
)

print(
    "Salary:",
    analysis.salary_min,
    analysis.salary_max,
    analysis.salary_currency,
)

print()

print("EVIDENCE")

for item in analysis.evidence:
    print("-", item)

print()

print("CONCERNS")

for item in analysis.concerns:
    print("-", item)