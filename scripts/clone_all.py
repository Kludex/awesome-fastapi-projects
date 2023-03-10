import shutil

import git
from git.repo.base import Repo
from giturlparse import parse
import os

with open("unique_links.txt") as fp:
    links = fp.readlines()
    for i, link in enumerate(links, start=1):
        link = link.rstrip()
        owner = parse(link).owner
        name = parse(link).name
        repo_dir = f"reps/{owner}|{name}"
        if os.path.exists(repo_dir):
            print(f"File num: {i} - {owner}/{name} - directory already exists, skipping...")
        else:
            print(f"File num: {i} - {owner}/{name}")
            try:
                Repo.clone_from(link, f"reps/{owner}|{name}")
            except Exception as e:
                print(f"Exception {e}")