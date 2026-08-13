from requirement_parser import parse_requirements


request = """
Find remote junior data analyst jobs in India.
I have about 1 year of experience and know Excel and SQL.
I prefer full-time positions.
"""


job_requirements, candidate_profile = parse_requirements(
    request
)


print()
print("JOB REQUIREMENTS")
print(job_requirements)

print()
print("CANDIDATE PROFILE")
print(candidate_profile)