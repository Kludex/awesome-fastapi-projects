import json
import re
from typing import Dict, Union

f_in = open("imports.txt", "r")

mp: Dict[str, Union[set, list]] = {}

for line in f_in.readlines():
    try:
        rep_name = line.split("/")[1]
    except IndexError:
        rep_name = ""
    mp[rep_name] = mp.get(rep_name, set())
    result = re.search(r"from (\w+)[\.\w+]*|:[ ]*import (\w*)\n", line)
    if result:
        if result.group(1):
            mp[rep_name].add(result.group(1))
        if result.group(2):
            mp[rep_name].add(result.group(2))

for key in mp:
    mp[key] = list(mp[key])

with open("results.json", "w") as f:
    json.dump(mp, f, sort_keys=True, indent=2)

print(len(mp))
f_in.close()
