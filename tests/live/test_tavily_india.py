import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise RuntimeError(
        "TAVILY_API_KEY is not configured."
    )

client = TavilyClient(
    api_key=api_key
)


queries = [
    'site:job-boards.greenhouse.io "Data Analyst" "India"',
    'site:job-boards.greenhouse.io "Data Analyst I" "India"',
    'site:job-boards.greenhouse.io "Associate Data Analyst" "India"',

    'site:jobs.lever.co "Data Analyst" "India"',
    'site:jobs.lever.co "Junior Data Analyst" "India"',
    'site:jobs.lever.co "Data Analyst I" "India"',

    'site:jobs.ashbyhq.com "Data Analyst" "India"',
    'site:jobs.ashbyhq.com "Data Analyst I" "India"',
    'site:jobs.ashbyhq.com "Associate Data Analyst" "India"',
]


for query in queries:

    print()
    print("=" * 80)
    print("QUERY:")
    print(query)
    print("=" * 80)

    try:

        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5,
            topic="general",
            include_answer=False,
            include_raw_content=False,
        )

        results = response.get(
            "results",
            [],
        )

        print(
            "RESULTS:",
            len(results),
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            print()
            print(index)
            print(
                "TITLE:",
                result.get("title"),
            )
            print(
                "URL:",
                result.get("url"),
            )
            print(
                "CONTENT:",
                (
                    result.get("content", "")
                    [:500]
                    .replace("\n", " ")
                ),
            )

    except Exception as error:

        print(
            "SEARCH ERROR:",
            error,
        )