from job_enricher import fetch_job_page


url = (
    "https://job-boards.greenhouse.io/"
    "arcadiacareers/jobs/8620471002"
)


text = fetch_job_page(
    url
)


print(
    "EXTRACTED CHARACTERS:",
    len(text),
)


print()
print(
    "FIRST 3000 CHARACTERS:"
)


print(
    text[:3000]
)