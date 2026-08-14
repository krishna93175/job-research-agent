from web_normalizer import clean_url


tests = [
    "[https://example.com/job](https://example.com/job)",
    "https://example.com/job",
    "Some text https://example.com/job more text",
]


for value in tests:
    result = clean_url(value)

    print("INPUT :", repr(value))
    print("OUTPUT:", repr(result))
    print()