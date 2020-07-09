from typing import List
import json
from pytablewriter import MarkdownTableWriter
from stdlib_list import stdlib_list

NATIVE = ["fastapi", "starlette", "pydantic", "typing", "uvicorn", "app"]


def filter_list(dependencies: List[str]) -> List[str]:
    return [
        dependency
        for dependency in dependencies
        if not (
            dependency in NATIVE
            or dependency in stdlib_list("3.8")
            or dependency.startswith("_")
        )
    ]


def format_with_link(project: str) -> str:
    links = open("unique_links.txt", "r")
    for link in links.readlines():
        if project in link:
            return f"[{project}]({link})"

with open("results.json") as json_file:
    data = json.load(json_file)
    writer = MarkdownTableWriter()
    writer.headers = ["Project", "Dependencies"]
    writer.value_matrix = [
        [format_with_link(project), filter_list(dependencies)]
        for project, dependencies in data.items()
        if (
            len(filter_list(dependencies)) > 0
            and len(filter_list(dependencies)) < 20
            and project != ""
        )
    ]
    writer.write_table()
