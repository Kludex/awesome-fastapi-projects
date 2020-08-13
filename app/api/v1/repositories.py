from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
def get_repositories():  # Paginate
    """
    # TODO: Decide the sorted key. Maybe should use the votes at some point.
    Retrieves a sorted list of repositories. The sorted key is the number of
    stars the repository have on GitHub.

    This endpoint is used to generate the `home page`.
    """


@router.get("/{repo_id}")  # , response_model=Repository)
def get_repository(repo_id: int):
    """
    Retrieves a repository given its ID.

    This endpoint is used to generate the `single repository page`.
    """


# User needs to be logged in with GitHub account
@router.post("/{repo_id}/vote")
def post_vote(repo_id: int, vote: bool = Query(...)):
    """
    Sends a vote from an authenticated GitHub user to the requested repository
    given its ID.

    This endpoint is used when a user votes on the repository.
    """
    pass


@router.get("/search/{package}")  # , response_model=List[Repository])
def get_search(package: str):  # Paginate
    """
    Retrieves a list of repositories that uses the requested `package`.

    This endpoint is used to generate the `repository search page`.
    """
    # return crud_repositories.get_multi(session, package=package)
