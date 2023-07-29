"""Factories for creating models for testing."""
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from app.models import DependencyCreateData, RepoCreateData


@register_fixture
class DependencyCreateDataFactory(ModelFactory[DependencyCreateData]):
    """Factory for creating DependencyCreateData."""

    __model__ = DependencyCreateData


@register_fixture
class RepoCreateDataFactory(ModelFactory[RepoCreateData]):
    """Factory for creating RepoCreateData."""

    __model__ = RepoCreateData

    __randomize_collection_length__ = True
    __min_collection_length__ = 2
    __max_collection_length__ = 5
