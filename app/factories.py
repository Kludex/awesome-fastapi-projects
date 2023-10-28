"""Factories for creating models for testing."""
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from app.models import DependencyCreateData


@register_fixture
class DependencyCreateDataFactory(ModelFactory[DependencyCreateData]):
    """Factory for creating DependencyCreateData."""

    __model__ = DependencyCreateData
