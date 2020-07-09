import shutil

import git
from git.repo.base import Repo
from giturlparse import parse

# class Progress(git.remote.RemoteProgress):
#     def update(self, op_code, cur_count, max_count=None, message=''):
#         print(self._cur_line)

with open("unique_links.txt") as fp:
    links = fp.readlines()
    for i, link in enumerate(links, start=1):
        link = link.rstrip()
        name = parse(link).name
        print(f"File num: {i}")
        Repo.clone_from(link, name)
        try:
            shutil.move(name, "reps")
        except:
            shutil.rmtree(name)
