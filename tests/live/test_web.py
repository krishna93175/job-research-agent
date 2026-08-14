import json

from web_discovery import search_web


query = """
Find remote junior data analyst jobs in India.
Prefer actual job listings and company career pages.
"""


result = search_web(query)

print()
print("RAW JSON")
print(result)

print()

try:
    data = json.loads(result)

    print("NUMBER OF JOBS:", len(data.get("jobs", [])))

    for number, job in enumerate(
        data.get("jobs", []),
        start=1,
    ):
        print()
        print(f"{number}. {job.get('title')}")
        print(f"   Company: {job.get('company')}")
        print(f"   Location: {job.get('location')}")
        print(f"   Remote: {job.get('remote')}")
        print(f"   Source: {job.get('source')}")
        print(f"   URL: {job.get('url')}")

except json.JSONDecodeError as error:
    print()
    print("JSON PARSING FAILED")
    print(error)