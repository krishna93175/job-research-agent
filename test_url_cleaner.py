from web_discovery import clean_url


tests = [
    "[https://example.com/job](https://example.com/job)",
    "https://example.com/job",
    "Some text [https://example.com/job](https://example.com/job)",
    "[https://in.linkedin.com/jobs/view/junior-data-analyst-at-blu-careers-4231015087](https://in.linkedin.com/jobs/view/junior-data-analyst-at-blu-careers-4231015087)",
]


for value in tests:
    print("INPUT :", repr(value))
    print("OUTPUT:", repr(clean_url(value)))
    print()