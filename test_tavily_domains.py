import os

from dotenv import load_dotenv
from tavily import TavilyClient

from web_discovery import (
    clean_url,
    is_likely_job_listing_url,
)


load_dotenv()


# =================================================
# Configuration
# =================================================

api_key = os.getenv(
    "TAVILY_API_KEY"
)

if not api_key:
    raise RuntimeError(
        "TAVILY_API_KEY is not configured."
    )


client = TavilyClient(
    api_key=api_key
)


# =================================================
# Targeted ATS queries
# =================================================

queries = [
    (
        "GREENHOUSE",
        'site:job-boards.greenhouse.io '
        '"Junior Data Analyst" India remote',
    ),
    (
        "LEVER",
        'site:jobs.lever.co '
        '"Junior Data Analyst" India remote',
    ),
    (
        "ASHBY",
        'site:jobs.ashbyhq.com '
        '"Data Analyst" India remote',
    ),
]


# =================================================
# Search
# =================================================

for source_name, query in queries:

    print()
    print("=" * 80)
    print(source_name)
    print("=" * 80)

    print(
        "QUERY:",
        query,
    )

    try:

        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5,
            topic="general",
            include_answer=False,
            include_raw_content=False,
        )

    except Exception as error:

        print()
        print(
            "TAVILY ERROR:",
            error,
        )

        continue

    results = response.get(
        "results",
        [],
    )

    print()
    print(
        "RESULTS:",
        len(results),
    )

    if not results:

        print(
            "No results returned."
        )

        continue

    # ---------------------------------------------
    # Display results
    # ---------------------------------------------

    for index, result in enumerate(
        results,
        1,
    ):

        title = result.get(
            "title",
            "",
        )

        raw_url = result.get(
            "url",
            "",
        )

        content = result.get(
            "content",
            "",
        )

        cleaned_url = clean_url(
            raw_url
        )

        is_job = (
            is_likely_job_listing_url(
                cleaned_url
            )
        )

        print()
        print(
            f"{index}."
        )

        print(
            "TITLE:",
            title,
        )

        print(
            "RAW URL:",
            raw_url,
        )

        print(
            "CLEAN URL:",
            cleaned_url,
        )

        print(
            "INDIVIDUAL JOB:",
            is_job,
        )

        print(
            "CONTENT:",
            content[:500]
            .replace(
                "\n",
                " ",
            )
        )


# =================================================
# Explicit URL classification tests
# =================================================

print()
print("=" * 80)
print("EXPLICIT ATS URL CLASSIFICATION TESTS")
print("=" * 80)


test_urls = [

    # ---------------------------------------------
    # Greenhouse
    # ---------------------------------------------

    (
        True,
        "http://job-boards.greenhouse.io/"
        "yipitdata/jobs/7844012",
    ),

    (
        False,
        "http://job-boards.greenhouse.io/"
        "ethoslife",
    ),

    (
        True,
        "https://job-boards.greenhouse.io/"
        "upstart/jobs/7979136",
    ),

    # ---------------------------------------------
    # Lever
    # ---------------------------------------------

    (
        True,
        "https://jobs.lever.co/"
        "totalsystech/"
        "e96d1334-8c05-443a-a866-1c9b00bc9638/"
        "apply",
    ),

    (
        False,
        "https://jobs.lever.co/"
        "weloglobal",
    ),

    (
        False,
        "https://jobs.lever.co/"
        "binance",
    ),

    # ---------------------------------------------
    # Ashby
    # ---------------------------------------------

    (
        True,
        "https://jobs.ashbyhq.com/"
        "parker/"
        "d66365a5-5e06-4091-9e9b-ccc5d83955df",
    ),

    (
        True,
        "https://jobs.ashbyhq.com/"
        "harvey/"
        "e69f2050-b4c0-4fbb-9852-2c60d2adbb45",
    ),

    (
        False,
        "https://jobs.ashbyhq.com/"
        "kraken.com",
    ),

    (
        False,
        "https://jobs.ashbyhq.com/"
        "hinge-health",
    ),
]


passed = 0
failed = 0


for expected, url in test_urls:

    actual = is_likely_job_listing_url(
        url
    )

    status = (
        "PASS"
        if actual == expected
        else "FAIL"
    )

    print()
    print(
        status,
        "| Expected:",
        expected,
        "| Actual:",
        actual,
    )

    print(
        "URL:",
        url,
    )

    if actual == expected:
        passed += 1
    else:
        failed += 1


# =================================================
# Final result
# =================================================

print()
print("=" * 80)
print("URL CLASSIFICATION SUMMARY")
print("=" * 80)

print(
    "PASSED:",
    passed,
)

print(
    "FAILED:",
    failed,
)

if failed == 0:

    print()
    print(
        "ATS URL CLASSIFICATION TEST: PASSED"
    )

else:

    print()
    print(
        "ATS URL CLASSIFICATION TEST: FAILED"
    )