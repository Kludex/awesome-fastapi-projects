"""Test the client module of the scraper app."""
import pytest
from dirty_equals import HasLen, IsDatetime, IsInstance, IsPositiveInt
from pydantic import Json, TypeAdapter

from app.scraper.client import SourceGraphRepoData


@pytest.fixture()
def source_graph_matched_repos_data() -> Json:
    """Return the sample data of the matched repositories."""
    return [
        {
            "type": "repo",
            "repositoryID": 55636527,
            "repository": "github.com/tiangolo/sqlmodel",
            "repoStars": 10277,
            "repoLastFetched": "2023-07-31T18:47:22.875731Z",
            "description": (
                "SQL databases in Python, designed "
                "for simplicity, compatibility, "
                "and robustness."
            ),
            "metadata": {
                "fastapi": "null",
                "json": "null",
                "json-schema": "null",
                "pydantic": "null",
                "python": "null",
                "sql": "null",
                "sqlalchemy": "null",
            },
        },
        {
            "type": "repo",
            "repositoryID": 59434622,
            "repository": "github.com/reflex-dev/reflex",
            "repoStars": 10061,
            "repoLastFetched": "2023-07-31T08:58:42.692906Z",
            "description": "(Previously Pynecone) 🕸 Web apps in pure Python 🐍",
        },
        {
            "type": "repo",
            "repositoryID": 42982149,
            "repository": "github.com/PaddlePaddle/PaddleNLP",
            "repoStars": 9804,
            "repoLastFetched": "2023-07-31T16:48:08.839209Z",
            "description": (
                "👑 Easy-to-use and powerful NLP library with 🤗 "
                "Awesome model zoo, supporting wide-range of NLP tasks "
                "from research to industrial applications, including"
                " 🗂Text Classification, 🔍 Neural Search, ❓ Question "
                "Answering, ℹ️ Information Extraction, "
                "📄 Document Intelligence, 💌 Sentiment Analysis etc."
            ),
            "metadata": {
                "bert": "null",
                "embedding": "null",
                "ernie": "null",
                "information-extraction": "null",
                "neural-search": "null",
                "nlp": "null",
                "paddlenlp": "null",
                "pretrained-models": "null",
                "question-answering": "null",
                "search-engine": "null",
                "semantic-analysis": "null",
                "sentiment-analysis": "null",
                "seq2seq": "null",
                "transformer": "null",
                "transformers": "null",
                "uie": "null",
            },
        },
        {
            "type": "repo",
            "repositoryID": 36246068,
            "repository": "github.com/realpython/materials",
            "repoStars": 4359,
            "repoLastFetched": "2023-07-31T05:15:16.993896Z",
        },
    ]


def test_source_graph_repo_data(source_graph_matched_repos_data: Json) -> None:
    """Test the SourceGraphRepoData deserialization."""
    assert source_graph_matched_repos_data == HasLen(4)
    _SourceGraphRepoDataListValidator = TypeAdapter(list[SourceGraphRepoData])
    repos_parsed = _SourceGraphRepoDataListValidator.validate_python(
        source_graph_matched_repos_data
    )
    assert repos_parsed == HasLen(4)
    assert all(repo == IsInstance[SourceGraphRepoData] for repo in repos_parsed)
    assert all(
        repo.repo_id == repo_data["repositoryID"]
        for repo, repo_data in zip(
            repos_parsed, source_graph_matched_repos_data, strict=True
        )
    )
    assert all(
        repo.repo_handle == repo_data["repository"]
        for repo, repo_data in zip(
            repos_parsed, source_graph_matched_repos_data, strict=True
        )
    )
    assert all(
        repo.stars == IsPositiveInt and repo.stars == repo_data["repoStars"]
        for repo, repo_data in zip(
            repos_parsed, source_graph_matched_repos_data, strict=True
        )
    )
    assert all(
        str(repo.repo_url) == f"https://{repo_data['repository']}"
        for repo, repo_data in zip(
            repos_parsed, source_graph_matched_repos_data, strict=True
        )
    )
    assert all(repo.last_fetched_at == IsDatetime for repo in repos_parsed)
