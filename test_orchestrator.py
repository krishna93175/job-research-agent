from orchestrator import (
    run_job_search,
    print_results,
)


query = """
Find remote junior data analyst jobs in India.
I have 1 year of experience and skills in
Excel and SQL. I want full-time positions.
"""


result = run_job_search(
    query,
    analysis_limit=1,
)


print_results(result)