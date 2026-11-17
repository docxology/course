"""Curriculum Repository System public compatibility exports."""

__version__ = "0.1.0"
__author__ = "Curriculum Repository Team"
from curriculum import tools
from curriculum.accessibility import (
    AccessibilityService,
)
from curriculum.ai import (
    AIFeaturesService,
    ContentCreationService,
    ResearchToolsService,
)
from curriculum.communication import (
    CollaborationService,
    CommunicationService,
)
from curriculum.config import settings
from curriculum.content import (
    ContentService,
    MetadataService,
    RenderingService,
    VersionControlService,
)
from curriculum.content_generation import (
    ContentGeneratorService,
    ContentQualityService,
    ContentWorkflowService,
)
from curriculum.core import (
    BaseEntity,
    Content,
    ContentAnalytics,
    ContentFormat,
    ContentStatus,
    ContentType,
    ContentVersion,
    DublinCore,
    LRMIMetadata,
    Metadata,
    PagedResponse,
    ResourceType,
    SessionAnalytics,
    SoftDeleteMixin,
    TimestampMixin,
    User,
    UserAnalytics,
    UserPermission,
    UserRole,
    UUIDMixin,
)
from curriculum.documentation import (
    DocumentationGeneratorService,
)
from curriculum.integration import (
    DistributionService,
    ExportService,
    GamificationService,
    IntegrationService,
)
from curriculum.learning import (
    ActivityVerb,
    AnalyticsReport,
    AnalyticsService,
    Assessment,
    AssessmentService,
    DeviceType,
    DifficultyLevel,
    EventType,
    GradingStatus,
    LearningEvent,
    ProgressService,
    Question,
    QuestionType,
    StudyToolsService,
    Submission,
    SubmissionResult,
)
from curriculum.mobile import (
    MobileService,
    OfflineService,
)
from curriculum.search import (
    SearchService,
    VisualizationService,
    WebsiteService,
)
from curriculum.teachers import (
    CourseManagementService,
    StudentManagementService,
    TeacherService,
)
from curriculum.users import (
    AuthenticationService,
    UserService,
)

__all__ = [
    "__version__",
    "__author__",
    "settings",
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
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    "tools",
]
