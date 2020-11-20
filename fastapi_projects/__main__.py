import json
import logging
import os
import re
import shutil
from datetime import datetime
from typing import List

from git import Git
from git.exc import GitCommandError
from github import Github
from github.Repository import Repository

logging.basicConfig(level=logging.INFO)

# Github
github_access_token = os.getenv("ACCESS_TOKEN_GITHUB")
g = Github(github_access_token)

MAX_SIZE = 100 * 1000  # 100 MB

# Directory
dir = os.getcwd()
clone_dir = os.path.join(dir, "tmp")
data_file = os.path.join(dir, "results.json")

INVALID_FOLDERS = ("site-packages", "venv")


# Functions
def clone(repository: Repository):
    try:
        clone_url = repository.clone_url
        Git(clone_dir).clone(clone_url)
    except GitCommandError:
        pass


def get_packages_from_file(path: str) -> List[str]:
    packages = set()
    logging.info("Reading file '%s'.", path)
    try:
        with open(path, "r") as file:
            for line in file.readlines():
                result = re.search(r"from (\w+)[\.\w+]*|:[ ]*import (\w*)\n", line)
                if result:
                    if result.group(1):
                        packages.add(result.group(1))
                    if result.group(2):
                        packages.add(result.group(2))
    except FileNotFoundError:
        logging.info("File not found '%s'.", path)
    except UnicodeDecodeError:
        logging.info("Invalid character on file '%s'.", path)
    return list(packages)


def extract_data(repository: Repository) -> dict:
    data = {}
    for (root, _, files) in os.walk(os.path.join(clone_dir, repository.name)):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(".py") and all(
                folder not in path for folder in INVALID_FOLDERS
            ):
                data["packages"] = get_packages_from_file(path)
    return data


def run():
    with open(data_file) as json_file:
        data = json.load(json_file)

    snippets = g.search_code('l=Python&q="from+fastapi+import+FastAPI"&type=Code')
    found = len(snippets)
    logging.info("Found '%d' snippets.", found)

    for i, snippet in enumerate(snippets):
        repository = snippet.repository
        name = repository.name
        owner = repository.owner
        logging.info("Got repository '%s' (%d / %d).", name, i + 1, found)

        if repository.id in data:
            commits = repository.get_commits()
            last_commit_date = [commit.commit.author.date for commit in commits][0]
            if (datetime.today() - last_commit_date).days > 7:
                logging.info("Repository '%s' already stored.", name)
                continue

        if repository.size > MAX_SIZE:
            logging.info("Repository size is '%d' MB. (SKIP)", repository.size // 1000)
            continue

        logging.info("Cloning repository '%s'.", name)
        clone(repository)

        logging.info("Extracting data from '%s'.", name)
        extracted_data = extract_data(repository)

        data[repository.id] = {"name": name, "owner": owner, **extracted_data}

        logging.info("Removing repository '%s'.", name)
        shutil.rmtree(os.path.join(clone_dir, name))

    logging.info("Writing on file!")
    with open(os.path.join(dir, "results.json"), "w") as json_file:
        json.dump(data, json_file)


# Run!
run()
