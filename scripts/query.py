import json
import os
import sys
from time import sleep
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo

import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("GITHUB_USERNAME")
password = os.getenv("GITHUB_PASSWORD")
API_URL = "https://api.github.com"

@on_exception(expo, RateLimitException, max_tries=20)
@limits(calls=30, period=60)
def get_response(page: int) -> dict:
    res = requests.get(
        f"{API_URL}/search/code",
        auth=(username, password),
        params={"q": "fastapi language:python stars:>1", "per_page": 100, "page": page},
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
page = int(sys.argv[1])
while True:
    sleep(2)
    print(f"Page: {page}")
    res = get_response(page)
    print(res.headers)
    res_json = res.json()
    print(res_json)
    if "items" in res_json:
        for item in res_json["items"]:
            file1.write(f"{item['repository'].get('html_url')}\n")

    if not 'next' in res.links.keys():
        print(f"Last page received is {page}, exiting query. If you want to continue from it call the script with the --continue option.")
        break   
    page += 1

file1.close()

with open(".checkpoint", "w") as f2:
    f2.write(str(page))