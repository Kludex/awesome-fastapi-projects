"""Factories for creating models for testing."""
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from app.models import RepoCreateData


@register_fixture
class RepoCreateDataFactory(ModelFactory[RepoCreateData]):
    """Factory for creating RepoCreateData."""

    __model__ = RepoCreateData
