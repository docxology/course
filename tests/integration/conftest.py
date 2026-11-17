"""Domain service fixtures for integration test suites."""

import pytest

from curriculum.ai.ai_features import AIFeaturesService
from curriculum.ai.content_creation import ContentCreationService
from curriculum.ai.research import ResearchToolsService
from curriculum.communication.collaboration import CollaborationService
from curriculum.communication.communication import CommunicationService
from curriculum.learning.progress import ProgressService
from curriculum.learning.study_tools import StudyToolsService


@pytest.fixture
def ai_features_service() -> AIFeaturesService:
    """Create an AIFeaturesService instance."""
    return AIFeaturesService()


@pytest.fixture
def content_creation_service() -> ContentCreationService:
    """Create a ContentCreationService instance."""
    return ContentCreationService()


@pytest.fixture
def research_service() -> ResearchToolsService:
    """Create a ResearchToolsService instance."""
    return ResearchToolsService()


@pytest.fixture
def progress_service() -> ProgressService:
    """Create a ProgressService instance."""
    return ProgressService()


@pytest.fixture
def study_tools_service() -> StudyToolsService:
    """Create a StudyToolsService instance."""
    return StudyToolsService()


@pytest.fixture
def communication_service() -> CommunicationService:
    """Create a CommunicationService instance."""
    return CommunicationService()


@pytest.fixture
def collaboration_service() -> CollaborationService:
    """Create a CollaborationService instance."""
    return CollaborationService()
