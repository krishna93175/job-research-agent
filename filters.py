from models import Job


def filter_jobs(
    jobs: list[Job],
    remote_required: bool = False,
    visa_required: bool = False,
) -> list[Job]:
    """
    Apply deterministic filters to a list of jobs.

    These filters should handle objective requirements before
    the AI evaluates the remaining jobs.
    """

    filtered_jobs = []

    for job in jobs:

        # Remote requirement
        if remote_required and not job.remote:
            continue

        # Visa sponsorship requirement
        if visa_required and job.visa_sponsorship is not True:
            continue

        filtered_jobs.append(job)

    return filtered_jobs