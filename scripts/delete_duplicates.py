f_in = open("links.txt", "r")
f_out = open("unique_links.txt", "w")
# Using a list instead of set to keep same order in links and unique_links urls
links = []

for line in f_in.readlines():
    if line not in links:
        links.append(line)

for link in links:
    f_out.write(link)

f_in.close()
f_out.close()
