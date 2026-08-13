from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    """
    Standardized representation of a job listing.
    """

    title: str
    company: str
    location: str

    remote: bool
    remote_scope: Optional[str]

    url: str
    source: str

    description: str

    visa_sponsorship: Optional[bool] = None
    remote_evidence: Optional[str] = None

    tags: list[str] = field(default_factory=list)
    job_types: list[str] = field(default_factory=list)

    source_evidence: list[str] = field(default_factory=list)


@dataclass
class JobRequirements:
    """
    Requirements describing the type of job the user wants.
    """

    role: Optional[str] = None
    location: Optional[str] = None

    remote_required: bool = False
    hybrid_allowed: bool = True

    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None

    employment_types: list[str] = field(default_factory=list)

    skills: list[str] = field(default_factory=list)

    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None

    applicant_country: Optional[str] = None

    visa_required: bool = False

    keywords: list[str] = field(default_factory=list)


@dataclass
class CandidateProfile:
    """
    Information about the person searching for a job.
    """

    experience_years: Optional[float] = None

    skills: list[str] = field(default_factory=list)

    education: list[str] = field(default_factory=list)

    current_country: Optional[str] = None

    desired_locations: list[str] = field(default_factory=list)

    desired_employment_types: list[str] = field(
        default_factory=list
    )


@dataclass
class JobAnalysis:
    """
    AI-generated structured analysis of a job posting.
    """

    role_relevance: str

    required_experience_min: Optional[float] = None
    required_experience_max: Optional[float] = None

    required_skills: list[str] = field(default_factory=list)

    employment_type: Optional[str] = None

    remote_status: Optional[str] = None
    remote_scope: Optional[str] = None

    location_requirements: Optional[str] = None

    visa_sponsorship: Optional[str] = None
    international_eligibility: Optional[str] = None

    evidence: list[str] = field(default_factory=list)

    concerns: list[str] = field(default_factory=list)