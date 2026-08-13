import re

from models import Job, JobRequirements


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: str | None) -> str:
    """
    Normalize text for matching.
    """

    if not value:
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def text_contains(
    text: str,
    value: str,
) -> bool:
    """
    Check whether a normalized value appears
    in normalized text.
    """

    text = normalize_text(text)
    value = normalize_text(value)

    if not value:
        return True

    return value in text


# ============================================================
# JOB TEXT
# ============================================================

def job_text(job: Job) -> str:
    """
    Combine searchable job fields into one string.
    """

    return " ".join(
        [
            job.title or "",
            job.company or "",
            job.location or "",
            job.description or "",
            " ".join(job.tags or []),
            " ".join(job.job_types or []),
            " ".join(job.source_evidence or []),
        ]
    )


def role_text(job: Job) -> str:
    """
    Return fields useful for determining the actual role.

    Role matching prioritizes the title and structured tags.
    """

    return normalize_text(
        " ".join(
            [
                job.title or "",
                " ".join(job.tags or []),
            ]
        )
    )


# ============================================================
# ROLE
# ============================================================

def matches_role(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Determine whether the job matches the requested role.
    """

    if not requirements.role:
        return True

    role = normalize_text(
        requirements.role
    )

    if not role:
        return True

    searchable = role_text(job)

    if not searchable:
        return True

    # Exact phrase match.
    if role in searchable:
        return True

    # Multi-word role:
    # every meaningful word must appear.
    role_words = [
        word
        for word in role.split()
        if len(word) > 2
    ]

    if not role_words:
        return True

    return all(
        word in searchable
        for word in role_words
    )


# ============================================================
# LOCATION
# ============================================================

def matches_location(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply location requirement.

    Unknown location does not automatically reject
    the job because some remote listings omit location
    from the normalized location field.
    """

    if not requirements.location:
        return True

    location = normalize_text(
        requirements.location
    )

    if not location:
        return True

    job_location = normalize_text(
        job.location
    )

    # Unknown location -> do not reject yet.
    #
    # The job may still contain location evidence in
    # its description/source evidence.
    if not job_location:

        evidence = normalize_text(
            " ".join(
                [
                    job.description or "",
                    job.remote_evidence or "",
                    " ".join(
                        job.source_evidence or []
                    ),
                ]
            )
        )

        if not evidence:
            return True

        return location in evidence

    return (
        location in job_location
        or job_location in location
    )


# ============================================================
# REMOTE
# ============================================================

def matches_remote(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply remote/hybrid requirements.
    """

    if requirements.remote_required:
        return job.remote is True

    return True


# ============================================================
# EMPLOYMENT TYPE
# ============================================================

def normalize_employment_type(
    value: str,
) -> str:
    """
    Normalize common employment-type labels.
    """

    value = normalize_text(value)

    replacements = {
        "full time": "full-time",
        "fulltime": "full-time",
        "full-time": "full-time",

        "part time": "part-time",
        "parttime": "part-time",
        "part-time": "part-time",

        "contractor": "contract",
        "contract position": "contract",
        "contract": "contract",

        "internship": "intern",
        "intern": "intern",

        "temporary": "temporary",
        "freelance": "freelance",
    }

    return replacements.get(
        value,
        value,
    )


def extract_known_employment_types(
    job: Job,
) -> set[str]:
    """
    Extract recognizable employment types.

    Unknown employment information is deliberately
    different from conflicting employment information.
    """

    found: set[str] = set()

    candidates = list(
        job.job_types or []
    )

    for candidate in candidates:

        normalized = normalize_employment_type(
            candidate
        )

        if normalized in {
            "full-time",
            "part-time",
            "contract",
            "intern",
            "temporary",
            "freelance",
        }:
            found.add(normalized)

    searchable = normalize_text(
        " ".join(
            [
                job.title or "",
                job.description or "",
                " ".join(
                    job.source_evidence or []
                ),
            ]
        )
    )

    # English
    if (
        "full time" in searchable
        or "full-time" in searchable
        or "fulltime" in searchable
    ):
        found.add("full-time")

    if (
        "part time" in searchable
        or "part-time" in searchable
        or "parttime" in searchable
    ):
        found.add("part-time")

    # German
    if "vollzeit" in searchable:
        found.add("full-time")

    if "teilzeit" in searchable:
        found.add("part-time")

    if "freelance" in searchable:
        found.add("freelance")

    if "internship" in searchable:
        found.add("intern")

    return found


def matches_employment_type(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply employment-type requirements.

    Unknown employment information does not reject
    a listing.

    Explicitly conflicting information does reject it.
    """

    if not requirements.employment_types:
        return True

    required_types = {
        normalize_employment_type(
            employment_type
        )
        for employment_type in requirements.employment_types
    }

    known_types = extract_known_employment_types(
        job
    )

    # No reliable employment information.
    if not known_types:
        return True

    # Explicitly known type must match.
    return bool(
        required_types.intersection(
            known_types
        )
    )


# ============================================================
# SKILLS
# ============================================================

def skill_evidence_text(
    job: Job,
) -> str:
    """
    Return only fields that can reasonably provide
    evidence about required skills.

    IMPORTANT:
    Company name and location are NOT skill evidence.
    """

    return normalize_text(
        " ".join(
            [
                job.description or "",
                " ".join(
                    job.tags or []
                ),
                " ".join(
                    job.source_evidence or []
                ),
            ]
        )
    )


def matches_skills(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply required-skill filtering.

    Critical behavior:

    - If the listing contains reliable skill evidence,
      required skills must be present.
    - If the listing contains no usable skill information,
      do NOT reject the job.
    """

    if not requirements.skills:
        return True

    searchable = skill_evidence_text(
        job
    )

    # --------------------------------------------------------
    # No skill information available.
    #
    # Do NOT reject.
    # --------------------------------------------------------

    if not searchable:
        return True

    # --------------------------------------------------------
    # Skill information exists.
    #
    # Now enforce all requested skills.
    # --------------------------------------------------------

    for skill in requirements.skills:

        normalized_skill = normalize_text(
            skill
        )

        if not normalized_skill:
            continue

        if normalized_skill not in searchable:
            return False

    return True


# ============================================================
# SALARY
# ============================================================

def matches_salary(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Salary filtering placeholder.

    Salary is currently analyzed later by the AI
    because the Job model does not reliably contain
    structured salary information.
    """

    return True


# ============================================================
# EXPERIENCE
# ============================================================

def matches_experience(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Experience filtering placeholder.

    Experience is analyzed later by the AI analyzer.
    """

    return True


# ============================================================
# VISA
# ============================================================

def matches_visa(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply visa requirement only when sponsorship
    information is explicitly available.
    """

    if not requirements.visa_required:
        return True

    if job.visa_sponsorship is None:
        return True

    return job.visa_sponsorship is True


# ============================================================
# COMPLETE REQUIREMENT CHECK
# ============================================================

def job_matches_requirements(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply all currently supported hard filters.
    """

    checks = [
        matches_role(
            job,
            requirements,
        ),

        matches_location(
            job,
            requirements,
        ),

        matches_remote(
            job,
            requirements,
        ),

        matches_employment_type(
            job,
            requirements,
        ),

        matches_skills(
            job,
            requirements,
        ),

        matches_salary(
            job,
            requirements,
        ),

        matches_experience(
            job,
            requirements,
        ),

        matches_visa(
            job,
            requirements,
        ),
    ]

    return all(checks)


# ============================================================
# FILTER JOBS
# ============================================================

def filter_jobs(
    jobs: list[Job],
    requirements: JobRequirements,
) -> list[Job]:
    """
    Return jobs satisfying the current hard requirements.
    """

    return [
        job
        for job in jobs
        if job_matches_requirements(
            job,
            requirements,
        )
    ]