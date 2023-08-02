"""Factories for creating test data."""
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from app.scraper.models import SourceGraphRepoData


@register_fixture
class SourceGraphRepoDataFactory(ModelFactory[SourceGraphRepoData]):
    """Factory for creating RepoCreateData."""

    __model__ = SourceGraphRepoData
