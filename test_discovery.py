from requirement_parser import parse_requirements
from job_discovery import discover_jobs


request = """
Find remote junior data analyst jobs in India.
I have about 1 year of experience and know Excel and SQL.
I prefer full-time positions.
"""


job_requirements, candidate_profile = parse_requirements(
    request
)


jobs = discover_jobs(
    job_requirements
)


print()
print("DISCOVERY RESULTS")
print(
    f"Unique jobs discovered: {len(jobs)}"
)

print()

for number, job in enumerate(
    jobs[:10],
    start=1,
):

    print(f"{number}. {job.title}")
    print(f"   Company: {job.company}")
    print(f"   Location: {job.location}")
    print(f"   Remote: {job.remote}")
    print(f"   URL: {job.url}")
    print()