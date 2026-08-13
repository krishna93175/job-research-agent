import requests


def fetch_jobs(
    search_term: str,
    remote_only: bool = False,
    visa_sponsorship: bool = False,
) -> list[dict]:
    """
    Retrieve raw jobs from the Arbeitnow API.
    """

    url = "https://www.arbeitnow.com/api/job-board-api"

    params = {
        "search": search_term,
    }

    if remote_only:
        params["remote"] = "true"

    if visa_sponsorship:
        params["visa_sponsorship"] = "true"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(
            f"Job search failed: {error}"
        )
        return []

    data = response.json()

    return data.get(
        "data",
        [],
    )