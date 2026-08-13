from models import Job


STRONG_MARKETING_TITLES = [
    "marketing specialist",
    "marketing coordinator",
    "marketing associate",
    "marketing assistant",
    "marketing executive",
    "marketing intern",
    "marketing manager",
    "digital marketing",
    "growth marketing",
    "content marketing",
    "social media marketing",
    "performance marketing",
    "product marketing",
    "email marketing",
    "brand marketing",
    "seo specialist",
    "seo manager",
    "seo intern",
    "content specialist",
    "content coordinator",
    "social media specialist",
    "social media coordinator",
]


MARKETING_TITLE_WORDS = [
    "marketing",
    "seo",
    "content",
    "social media",
    "growth",
    "communications",
]


NON_MARKETING_TITLE_WORDS = [
    "business analyst",
    "data analyst",
    "financial analyst",
    "software engineer",
    "solution architect",
    "sales engineer",
    "accountant",
    "developer",
    "designer",
    "trader",
    "consultant",
    "founders associate",
    "project manager",
]


def is_marketing_role(job: Job) -> bool:
    """
    Determine whether the primary role appears to be marketing-related.

    Title and tags are given substantially more weight than the description.
    """

    title = job.title.lower()
    tags = " ".join(job.tags).lower()

    # Explicitly reject obvious non-marketing job titles.
    if any(
        phrase in title
        for phrase in NON_MARKETING_TITLE_WORDS
    ):
        return False

    # Strong title match.
    if any(
        phrase in title
        for phrase in STRONG_MARKETING_TITLES
    ):
        return True

    # Marketing-related title terminology.
    title_match = any(
        phrase in title
        for phrase in MARKETING_TITLE_WORDS
    )

    # Marketing-related tags.
    tag_match = any(
        phrase in tags
        for phrase in MARKETING_TITLE_WORDS
    )

    return title_match or tag_match


def filter_marketing_jobs(jobs: list[Job]) -> list[Job]:
    """
    Keep jobs whose primary title or tags indicate marketing relevance.
    """

    return [
        job
        for job in jobs
        if is_marketing_role(job)
    ]