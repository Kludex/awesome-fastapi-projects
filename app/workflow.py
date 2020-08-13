from prefect import task, Flow


@task(name="Call GitHub API search")
def github_api_search():
    pass


@task(name="Scrap GitHub repositories")
def scrapy_github_repos():
    pass


with Flow("FastAPI Repositories") as flow:
    github_api_search()
    scrapy_github_repos()
