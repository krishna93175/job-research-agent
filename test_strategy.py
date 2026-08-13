from requirement_parser import parse_requirements
from search_strategy import build_search_queries


request = """
Find remote junior data analyst jobs in India.
I have about 1 year of experience and know Excel and SQL.
I prefer full-time positions.
"""


job_requirements, candidate_profile = parse_requirements(
    request
)


queries = build_search_queries(
    job_requirements
)


print("SEARCH QUERIES")
print()

for number, query in enumerate(
    queries,
    start=1,
):
    print(f"{number}. {query}")