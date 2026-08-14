from requirements import JobRequirements
from search_strategy import build_search_queries


requirements = JobRequirements(
    role="Data Analyst",
    location="India",
    remote_required=True,
    hybrid_allowed=True,
    min_experience_years=0,
    max_experience_years=2,
    employment_types=["Full-time"],
    skills=["Excel", "SQL"],
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    applicant_country="India",
    visa_required=False,
    keywords=[
        "remote",
        "junior",
        "data analyst",
    ],
)

queries = build_search_queries(requirements)

print("REQUIREMENTS:")
print(requirements)

print()
print("SEARCH QUERIES:")

for index, query in enumerate(queries, start=1):
    print(index, repr(query))

assert queries
assert any("data analyst" in query.lower() for query in queries)
assert any("india" in query.lower() for query in queries)
assert any("remote" in query.lower() for query in queries)

print()
print("SEARCH STRATEGY TEST: PASSED")