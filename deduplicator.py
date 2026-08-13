import re
from urllib.parse import urlparse

from models import Job


def normalize_text(value: str | None) -> str:
    """
    Normalize text for comparison.
    """

    if not value:
        return ""

    value = value.lower().strip()

    # Remove punctuation.
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    # Collapse multiple spaces.
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_url(url: str | None) -> str:
    """
    Normalize a URL for duplicate detection.
    """

    if not url:
        return ""

    url = url.strip()

    # Handle Markdown links.
    match = re.search(
        r"https?://[^\s\]\)>]+",
        url,
    )

    if match:
        url = match.group(0)

    parsed = urlparse(url)

    if not parsed.netloc:
        return url.lower().rstrip("/")

    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    return f"{host}{path}"


def job_key(job: Job) -> tuple:
    """
    Create a conservative identity key for a job.

    URL is preferred when available.
    Otherwise use company + title + location.
    """

    url = normalize_url(job.url)

    if url:
        return ("url", url)

    return (
        "details",
        normalize_text(job.company),
        normalize_text(job.title),
        normalize_text(job.location),
    )


def jobs_are_similar(job1: Job, job2: Job) -> bool:
    """
    Determine whether two jobs are probably the same listing.

    This is intentionally conservative.
    """

    company1 = normalize_text(job1.company)
    company2 = normalize_text(job2.company)

    title1 = normalize_text(job1.title)
    title2 = normalize_text(job2.title)

    location1 = normalize_text(job1.location)
    location2 = normalize_text(job2.location)

    # Company and title must match.
    if company1 != company2:
        return False

    if title1 != title2:
        return False

    # If both listings provide a location, require it to match.
    if location1 and location2:
        if location1 != location2:
            return False

    return True


def deduplicate_jobs(jobs: list[Job]) -> list[Job]:
    """
    Remove duplicate job listings.

    Keeps the first occurrence.
    """

    unique_jobs = []
    seen_keys = set()

    for job in jobs:

        key = job_key(job)

        if key in seen_keys:
            continue

        # Catch same job appearing under different URLs.
        duplicate = False

        for existing_job in unique_jobs:
            if jobs_are_similar(
                job,
                existing_job,
            ):
                duplicate = True
                break

        if duplicate:
            continue

        seen_keys.add(key)
        unique_jobs.append(job)

    return unique_jobs