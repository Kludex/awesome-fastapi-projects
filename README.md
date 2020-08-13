# Awesome FastAPI Projects

<!-- Insert a subtitle with by Marcelo Trylesinski and a link to LinkedIn -->

<!-- Insert FastAPI image with `Awesome` and `Projects` on it -->

<!-- Insert coverage and passing badges -->

In a world where the knowledge by itself is not a problem but finding the right information is, we decided to
create the **Awesome FastAPI Projects**: a web application that aims to show repositories using [FastAPI](tiangolo.fastapi.com).

If you arrived to this repository by mistake and what you really want is to find the FastAPI awesome curated list, 
you might want to check: [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi).

## Internal Workflow

**Awesome FastAPI Projects** have an internal workflow that is capable of getting the information about the repositories.

1. Gets the FastAPI repositories from GitHub API Search
2. Scraps the repositories that were retrieved on step 1 aiming to get the packages the repositories uses.

<!-- Add Prefect and Celery links -->
This workflow is created using [Prefect]() and [Celery]().

## Contributing

Pull requests are more than welcome.

If you're not sure if a feature will be accepted, create an issue.

# License

<!-- Insert link for `MIT License` to the license itself -->
This project is release under MIT License.
