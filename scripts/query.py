import json
import os
import sys
from time import sleep

import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("GITHUB_USERNAME")
password = os.getenv("GITHUB_PASSWORD")
API_URL = "https://api.github.com"


def get_response(page: int) -> dict:
    res = requests.get(
        f"{API_URL}/search/code",
        auth=(username, password),
        params={"q": "fastapi language:Python", "per_page": 100, "page": page},
    )
    return res


def get_next_link(link_header: str) -> str:
    return getattr(
        {
            rel: link
            for (link, rel) in re.findall(r'<(http.*?)>; rel="(.*?)"', link_header)
        },
        "next",
        None,
    )


filename = "links.txt"
file1 = open(filename, "a")  # append mode
has_next = True
page = 1
while has_next:
    sleep(1)
    res = get_response(page)
    res_json = res.json()
    if "items" in res_json:
        for item in res_json["items"]:
            file1.write(f"{item['repository']['html_url']}\n")
    print(f"Page: {page}")
    print(res.headers)
    # print(json.dumps(res_json, indent=4, sort_keys=True))
    # print(res.headers.get('X-RateLimit-Reset', 0))
    if int(
        res.headers.get("X-RateLimit-Remaining", 0)
    ) == 0 or "422" in res.headers.get("Status", "422"):
        has_next = False
    page += 1

file1.close()
