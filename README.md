# Curriculum Repository System

A comprehensive educational content management and delivery platform built with Python, designed to host, manage, and deliver educational content across multiple formats and platforms.

## Overview

The Curriculum Repository System is a modern, scalable platform for educational content management that implements industry standards including Dublin Core, LRMI metadata, SCORM packaging, and xAPI analytics. Built with a microservices-oriented architecture, it provides robust content authoring, version control, multi-format rendering, and comprehensive learning analytics.

## Features

### Content Management
- Multi-format content support (Markdown, HTML, LaTeX, PDF, SCORM, xAPI, H5P)
- Hierarchical content organization (Courses → Modules → Lessons)
- Git-based version control with semantic versioning
- Content lifecycle management (Draft → Review → Approved → Published → Archived)
- Full-text search and advanced filtering
- Tag and taxonomy-based organization

### User Management
- Role-based access control (Student, Instructor, Content Creator, Reviewer, Admin)
- Fine-grained permission system
- JWT-based authentication
- User groups and access control lists
- Activity tracking and session management

### Metadata & Standards
- Dublin Core 15-element metadata schema
- LRMI (Learning Resource Metadata Initiative) extensions
- Custom taxonomies and classification systems
- SEO optimization
- Accessibility compliance (WCAG 2.1)

### Assessment & Evaluation
- Multiple question types (Multiple Choice, True/False, Essay, Coding, etc.)
- Auto-grading capabilities
- Time-limited assessments
- Multiple attempts with tracking
- Comprehensive result analytics
- Question bank management

### Analytics & Reporting
- xAPI-compliant learning event tracking
- Real-time and batch analytics processing
- Content performance metrics
- User progress tracking
- Session analytics
- Exportable reports

### Rendering & Distribution
- Multi-format compilation (HTML5, PDF, EPUB, Mobile)
- SCORM package generation
- Progressive Web App support
- CDN-ready content delivery
- Offline capabilities

## Architecture

The system follows a highly modular architecture with separate modules for each domain:

```
src/curriculum/
├── core/                # Base classes and fundamental models
│   ├── base.py         # Base entities and mixins
│   ├── content.py      # Core content models
│   ├── user.py         # User models
│   └── metadata.py     # Metadata models
├── content/             # Content management services
│   ├── content.py      # Content CRUD operations
│   ├── metadata.py     # Metadata management
│   ├── rendering.py    # Multi-format rendering
│   └── version_control.py # Version control
├── learning/            # Learning and assessment services
│   ├── analytics.py    # Learning analytics
│   ├── assessment.py  # Assessment management
│   └── progress.py     # Progress tracking
├── users/              # User management and authentication
│   ├── user.py        # User service
│   └── authentication.py # Auth service
├── ai/                 # AI-powered features
│   ├── ai_features.py # Intelligent tutoring
│   ├── content_creation.py # AI content generation
│   └── research.py    # Research tools
├── communication/      # Communication features
│   ├── communication.py # Forums and messaging
│   └── collaboration.py # Group work
├── accessibility/      # Accessibility features
│   └── accessibility.py # WCAG compliance
├── mobile/             # Mobile and offline features
│   ├── mobile.py      # Mobile optimization
│   └── offline.py     # Offline capabilities
├── integration/        # External integrations
│   ├── integration.py # LMS integration
│   ├── distribution.py # Content distribution
│   ├── export.py      # Export formats
│   └── gamification.py # Gamification
├── search/             # Search and discovery
│   ├── search.py      # Elasticsearch integration
│   ├── visualization.py # Interactive charts
│   └── website.py     # Course websites
├── db/                 # Database layer
│   ├── base.py        # Database interface
│   ├── mongodb.py     # MongoDB adapter
│   └── postgresql.py  # PostgreSQL adapter
├── routes/             # API endpoints
│   ├── main.py        # FastAPI application
│   ├── content.py     # Content endpoints
│   ├── users.py       # User endpoints
│   └── analytics.py   # Analytics endpoints
├── tools/              # Utility functions
│   ├── validators.py  # Input validation
│   ├── formatters.py  # Data formatting
│   ├── security.py    # Security utilities
│   └── file_handling.py # File operations
├── config.py          # Configuration management
├── cli.py             # Command-line interface
└── orchestration.py   # Service coordination layer

tests/                   # Comprehensive test suite
├── core/               # Core module tests
├── content/            # Content module tests
├── learning/           # Learning module tests
├── ai/                 # AI module tests
├── communication/      # Communication tests
├── accessibility/      # Accessibility tests
├── mobile/             # Mobile tests
├── integration/        # Integration tests
├── search/             # Search tests
└── conftest.py         # Test configuration
```

### Modular Services

Each module contains specialized services:

**Core Services:**
- `BaseEntity`: Base entity with UUID, timestamps, soft delete
- `Content`: Educational content with lifecycle management
- `User`: User management with role-based permissions
- `Metadata`: Dublin Core and LRMI metadata standards

**Content Services:**
- `ContentService`: Content CRUD operations, lifecycle management
- `MetadataService`: Metadata management (Dublin Core, LRMI)
- `RenderingService`: Multi-format content rendering
- `VersionControlService`: Git-based content versioning

**Learning Services:**
- `AssessmentService`: Assessment creation and auto-grading
- `AnalyticsService`: xAPI-compliant learning event tracking
- `ProgressService`: Learning progress and adaptive paths

**AI Services:**
- `AIFeaturesService`: Intelligent tutoring and recommendations
- `ContentCreationService`: AI-assisted content generation
- `ResearchToolsService`: Citation and bibliography management

**Communication Services:**
- `CommunicationService`: Forums, messaging, announcements
- `CollaborationService`: Group projects and peer review

**Integration Services:**
- `IntegrationService`: LMS integration (Canvas, Moodle, etc.)
- `ExportService`: Multi-format export (PDF, SCORM, EPUB)
- `GamificationService`: Points, badges, leaderboards

**Search & Discovery:**
- `SearchService`: Elasticsearch-based full-text search
- `VisualizationService`: Interactive charts and knowledge maps
- `WebsiteService`: Course website generation

## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+ (for relational data)
- MongoDB 6+ (for content storage)
- Redis 7+ (for caching)
- Elasticsearch 8+ (optional, for search)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/curriculum-repository.git
cd curriculum-repository
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize databases:
```bash
# Run database migrations (when implemented)
alembic upgrade head
```

6. Run tests:
```bash
pytest
```

7. Start development server:
```bash
uvicorn curriculum.api.main:app --reload
```

## Usage

### Creating Content

```python
from curriculum.services import ContentService
from curriculum.models.content import ContentType, ContentFormat

content_service = ContentService()

content = content_service.create_content(
    title="Introduction to Python",
    content_type=ContentType.LESSON,
    format=ContentFormat.MARKDOWN,
    author_id=user_id,
    description="Learn Python basics",
    content_body="# Python Basics\n\nPython is a programming language."
)
```

### Managing Users

```python
from curriculum.services import UserService, AuthenticationService
from curriculum.models.user import UserRole

user_service = UserService()
auth_service = AuthenticationService(user_service)

# Create user
user = user_service.create_user(
    email="student@example.com",
    username="student",
    full_name="Student Name",
    password="secure_password",
    roles=[UserRole.STUDENT]
)

# Authenticate
authenticated_user = auth_service.authenticate_user("student", "secure_password")
access_token = auth_service.create_access_token(authenticated_user.id)
```

### Creating Assessments

```python
from curriculum.services import AssessmentService
from curriculum.models.assessment import QuestionType

assessment_service = AssessmentService()

# Create assessment
assessment = assessment_service.create_assessment(
    title="Python Quiz",
    description="Test your Python knowledge",
    time_limit=30
)

# Add question
question = assessment_service.create_question(
    title="What is Python?",
    question_text="Select the correct description.",
    question_type=QuestionType.MULTIPLE_CHOICE,
    points=10.0,
    correct_answer="A programming language",
    options=[
        {"id": "a", "text": "A programming language"},
        {"id": "b", "text": "A snake"},
    ]
)

assessment_service.add_question_to_assessment(assessment.id, question.id)
```

### Tracking Analytics

```python
from curriculum.services import AnalyticsService
from curriculum.models.analytics import ActivityVerb, EventType

analytics_service = AnalyticsService()

# Track content view
analytics_service.track_content_view(
    user_id=user.id,
    content_id=content.id,
    duration=300
)

# Generate report
report = analytics_service.generate_user_report(user.id)
```

## Testing

The project follows Test-Driven Development (TDD) with comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_content_service.py

# Run tests by marker
pytest -m unit
pytest -m integration
```

## Development

### Code Quality

The project maintains high code quality standards:

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

### Project Standards

- **Type hints**: All functions include type annotations
- **Docstrings**: Google-style docstrings for all public APIs
- **Testing**: Minimum 80% code coverage
- **Code style**: Black formatting, 100 character line length
- **Commits**: Conventional commit messages

## API Documentation

API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running the server.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Implement your changes
5. Ensure tests pass (`pytest`)
6. Ensure code quality (`black`, `flake8`, `mypy`)
7. Commit your changes (`git commit -m 'feat: add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built following educational technology standards:
- Dublin Core Metadata Initiative
- LRMI (Learning Resource Metadata Initiative)
- SCORM (Sharable Content Object Reference Model)
- xAPI (Experience API / Tin Can API)
- QTI (Question & Test Interoperability)
- WCAG 2.1 (Web Content Accessibility Guidelines)

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Status**: Alpha - Active Development

**Version**: 0.1.0

**Last Updated**: September 2025
