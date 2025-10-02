"""Curriculum Repository System - A comprehensive educational content management platform."""

__version__ = "0.1.0"
__author__ = "Curriculum Repository Team"

from curriculum.config import settings

# Import all core models and services
from curriculum.core import *
from curriculum.content import *
from curriculum.learning import *
from curriculum.users import *
from curriculum.ai import *
from curriculum.communication import *
from curriculum.accessibility import *
from curriculum.mobile import *
from curriculum.integration import *
from curriculum.search import *
from curriculum.teachers import *
from curriculum.content_generation import *
from curriculum.documentation import *

# Import tools module to make it accessible
from curriculum import tools

__all__ = [
    "__version__",
    "__author__",
    "settings",
    # Re-export all models and services for backward compatibility
    "BaseEntity",
    "PagedResponse",
    "Content",
    "ContentVersion",
    "ContentStatus",
    "ContentFormat",
    "ContentType",
    "Metadata",
    "DublinCore",
    "LRMIMetadata",
    "ResourceType",
    "User",
    "UserRole",
    "UserPermission",
    "LearningEvent",
    "AnalyticsReport",
    "ActivityVerb",
    "EventType",
    "DeviceType",
    "ContentAnalytics",
    "UserAnalytics",
    "SessionAnalytics",
    "Assessment",
    "Question",
    "Submission",
    "SubmissionResult",
    "QuestionType",
    "DifficultyLevel",
    "GradingStatus",
    "ContentService",
    "UserService",
    "AuthenticationService",
    "MetadataService",
    "AssessmentService",
    "AnalyticsService",
    "RenderingService",
    "VersionControlService",
    "VisualizationService",
    "WebsiteService",
    "StudyToolsService",
    "ProgressService",
    "ExportService",
    "ResearchToolsService",
    "AIFeaturesService",
    "CommunicationService",
    "CollaborationService",
    "AccessibilityService",
    "MobileService",
    "OfflineService",
    "ProgressService",
    "GamificationService",
    "DistributionService",
    "IntegrationService",
    "SearchService",
    "ContentCreationService",
    "TeacherService",
    "CourseManagementService",
    "StudentManagementService",
    "ContentGeneratorService",
    "ContentWorkflowService",
    "ContentQualityService",
    "DocumentationGeneratorService",
]