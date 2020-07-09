f_in = open("links.txt", "r")
f_out = open("unique_links.txt", "w")

links = set()

for line in f_in.readlines():
    links.add(line)

for link in links:
    f_out.write(link)

f_in.close()
f_out.close()
