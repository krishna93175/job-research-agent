from models import Job
from web_normalizer import clean_url


def normalize_job(raw_job: dict) -> Job:
    """
    Convert a raw job listing into our standardized Job model.

    Supports common field-name variations used by different
    job sources.
    """

    # -------------------------
    # Basic fields
    # -------------------------

    title = (
        raw_job.get("title")
        or raw_job.get("job_title")
        or "Unknown"
    )

    company = (
        raw_job.get("company")
        or raw_job.get("company_name")
        or raw_job.get("employer")
        or "Unknown"
    )

    location = (
        raw_job.get("location")
        or raw_job.get("locations")
        or "Unknown"
    )

    # -------------------------
    # Remote status
    # -------------------------

    remote_value = raw_job.get("remote")

    if isinstance(remote_value, str):
        remote = remote_value.lower() in {
            "true",
            "yes",
            "remote",
        }
    else:
        remote = bool(remote_value)

    # -------------------------
    # URL
    # -------------------------

    url = clean_url(
        raw_job.get("url")
        or raw_job.get("job_url")
        or raw_job.get("apply_url")
        or ""
    )

    # -------------------------
    # Description
    # -------------------------

    description = (
        raw_job.get("description")
        or raw_job.get("job_description")
        or ""
    )

    # -------------------------
    # Tags
    # -------------------------

    tags = raw_job.get("tags") or []

    if not isinstance(tags, list):
        tags = [str(tags)]

    # -------------------------
    # Job types
    # -------------------------

    job_types = (
        raw_job.get("job_types")
        or raw_job.get("employment_types")
        or []
    )

    if not isinstance(job_types, list):
        job_types = [str(job_types)]

    # -------------------------
    # Create standardized Job
    # -------------------------

    return Job(
        title=title,
        company=company,
        location=location,
        remote=remote,
        remote_scope=None,
        visa_sponsorship=None,
        url=url,
        source=raw_job.get(
            "source",
            "Arbeitnow",
        ),
        description=description,
        tags=tags,
        job_types=job_types,
    )