import re

from models import Job


def clean_url(url: str) -> str:
    """
    Extract a plain HTTP/HTTPS URL from a possibly
    Markdown-formatted or otherwise wrapped string.
    """

    if not url:
        return ""

    url = str(url).strip()

    url = url.replace(
        "\\(",
        "(",
    )

    url = url.replace(
        "\\)",
        ")",
    )

    url = url.replace(
        "\\[",
        "[",
    )

    url = url.replace(
        "\\]",
        "]",
    )

    url = url.replace(
        "\\\n",
        "",
    )

    url = url.replace(
        "\n",
        "",
    )

    url = url.replace(
        "\r",
        "",
    )

    match = re.search(
        r"https?://[^\s<>\[\]\"']+",
        url,
        flags=re.IGNORECASE,
    )

    if not match:
        return url.strip()

    result = match.group(0).strip()

    result = result.rstrip(
        ".,;:!?)}>'\""
    )

    return result


def get_source_from_url(
    url: str,
    reported_source: str | None = None,
) -> str:
    """
    Determine the job source from the URL.
    """

    url_lower = url.lower()

    if "linkedin." in url_lower:
        return "LinkedIn"

    if "indeed." in url_lower:
        return "Indeed"

    if "greenhouse.io" in url_lower:
        return "Greenhouse"

    if "lever.co" in url_lower:
        return "Lever"

    if "ashbyhq.com" in url_lower:
        return "Ashby"

    if "workday" in url_lower:
        return "Workday"

    if reported_source:
        return reported_source

    return "Unknown"


def _normalize_remote(
    value,
) -> bool:
    """
    Convert supported remote values to a boolean.
    Unknown values remain False because the Job model
    requires a boolean.
    """

    if isinstance(
        value,
        bool,
    ):
        return value

    if value is None:
        return False

    if isinstance(
        value,
        str,
    ):

        return value.strip().lower() in {
            "true",
            "yes",
            "remote",
        }

    return bool(value)


def _build_job_types(
    employment_type,
) -> list[str]:
    """
    Convert extracted employment type into the format
    used by the existing Job model.
    """

    if not employment_type:
        return []

    value = str(
        employment_type
    ).strip()

    if not value:
        return []

    normalized = value.lower()

    if (
        "full" in normalized
        and "time" in normalized
    ):
        return [
            "full-time"
        ]

    if "part" in normalized:
        return [
            "part-time"
        ]

    if "contract" in normalized:
        return [
            "contract"
        ]

    if (
        "intern" in normalized
        or "internship" in normalized
    ):
        return [
            "internship"
        ]

    if "freelance" in normalized:
        return [
            "freelance"
        ]

    return [
        value
    ]


def _infer_remote_scope(
    location,
    remote_scope,
    remote_evidence,
) -> str | None:
    """
    Preserve the geographic scope of a remote job.
    """

    if remote_scope:
        return str(
            remote_scope
        ).strip()

    combined = " ".join(
        str(value)
        for value in [
            location,
            remote_evidence,
        ]
        if value
    )

    if not combined:
        return None

    lower = combined.lower()

    if "india" in lower:
        return "India"

    if "canada" in lower:
        return "Canada"

    if (
        "united states" in lower
        or "remote - us" in lower
        or "remote us" in lower
    ):
        return "US"

    if "uk" in lower:
        return "UK"

    if "worldwide" in lower:
        return "Worldwide"

    return None


def normalize_web_job(
    data: dict,
) -> Job:
    """
    Convert a web-discovered job dictionary into
    the standardized Job model.

    Preserves:

    - location
    - remote scope
    - remote evidence
    - employment type
    - description
    - source evidence
    """

    url = clean_url(
        data.get(
            "url",
            "",
        )
    )

    remote = _normalize_remote(
        data.get(
            "remote"
        )
    )

    location = data.get(
        "location"
    )

    if not location:
        location = (
            "Unknown location"
        )

    remote_evidence = data.get(
        "remote_evidence"
    )

    remote_scope = _infer_remote_scope(
        location,
        data.get(
            "remote_scope"
        ),
        remote_evidence,
    )

    employment_type = data.get(
        "employment_type"
    )

    job_types = _build_job_types(
        employment_type
    )

    description = data.get(
        "description",
        "",
    )

    if description is None:
        description = ""

    location_evidence = data.get(
        "location_evidence"
    )

    source_evidence = []

    if location_evidence:
        source_evidence.append(
            str(
                location_evidence
            )
        )

    if remote_evidence:
        source_evidence.append(
            str(
                remote_evidence
            )
        )

    if employment_type:
        source_evidence.append(
            f"Employment type: "
            f"{employment_type}"
        )

    return Job(
        title=data.get(
            "title",
            "Unknown title",
        ),
        company=(
            data.get("company")
            or "Unknown company"
        ),
        location=(
            data.get("location")
            or "Unknown location"
        ),
        remote=remote,
        remote_scope=remote_scope,
        url=url,
        source=get_source_from_url(
            url,
            data.get(
                "source"
            ),
        ),
        description=str(
            description
        ),
        visa_sponsorship=None,
        remote_evidence=remote_evidence,
        tags=[],
        job_types=job_types,
        source_evidence=source_evidence,
    )