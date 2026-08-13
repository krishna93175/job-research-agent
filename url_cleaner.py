import re


def clean_url(url: str) -> str:
    if not url:
        return ""

    urls = re.findall(r"https?://[^\s\]\)>]+", str(url))

    if urls:
        return urls[-1].rstrip(").,;")

    return str(url).strip()
