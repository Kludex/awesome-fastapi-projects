import re
import sys

filename_in = sys.argv[1]
filename_out = sys.argv[2]
file_in = open(filename_in, "r")
lines = file_in.readlines()
file_out = open(filename_out, "w")

imports = set()

for line in lines:
    match1 = re.search(r"(from *(?!\.)(.+?)(?= |\.))", line)
    match2 = re.search(r"(: *(import) (.+))", line)
    if match1 is not None:
        imports.add(match1.group(2))
    if match2 is not None:
        imports.add(match2.group(3))


for imp in sorted(list(imports)):
    file_out.write(f"{imp}\n")
