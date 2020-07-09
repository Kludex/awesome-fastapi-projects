import json
from pytablewriter import MarkdownTableWriter

with open('results.json') as json_file:
    data = json.load(json_file)
    writer = MarkdownTableWriter()
    writer.headers = ["Project", "Dependencies"]
    writer.value_matrix = [
        (project, dependencies) for project, dependencies in data.items()
    ]
    writer.write_table()
