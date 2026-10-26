# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive test suite with 663+ tests across 33 test files
- GitHub Actions CI/CD pipeline with automated testing and security scanning
- Docker containerization with multi-service setup (PostgreSQL, MongoDB, Redis, Elasticsearch)
- Documentation generation system with LLM-enhanced analysis
- Modular architecture with 15+ specialized services
- Educational metadata standards (Dublin Core, LRMI, xAPI)
- Multi-format content rendering (HTML, PDF, Markdown, SCORM)
- Learning analytics and progress tracking
- Accessibility features (WCAG 2.1 compliance)
- Mobile and offline learning capabilities
- AI-powered content creation and analysis
- Research tools with citation management
- Communication and collaboration features
- Search and discovery functionality
- Integration capabilities (LMS, external APIs)

### Changed

- Migrated from setup.py to pyproject.toml as single source of truth
- Improved test organization with proper markers and fixtures
- Enhanced error handling and validation throughout
- Updated dependencies to latest stable versions
- Improved code quality with type hints and linting
- Refreshed pinned dependencies, GitHub Actions versions and Docker/Elasticsearch images
- Replaced archived `actions/create-release` / `actions/upload-release-asset` with `softprops/action-gh-release`
- Corrected repository URLs, branch workflow, Python version claims and contacts in README, CONTRIBUTING and CODE_OF_CONDUCT
- Replaced deprecated `datetime.utcnow()` examples in module guides with `datetime.now(timezone.utc)`

### Removed

- `PyPDF2` dependency (unused and superseded upstream by `pypdf`)
- Undeclared `pydantic-to-markdown` pin that made `pip install -r requirements.txt` unresolvable
- `alembic` (no migration environment or configuration exists in this repository)
- Stray nested `uv` project under `src/` (`src/pyproject.toml`, `src/uv.lock`, `src/main.py`, `src/.python-version`)
- Superseded `CRITICAL_FIXES_NEEDED.md` (every listed fix is recorded as applied in `FIXES_APPLIED.md`)
- Stale `*.py.backup` copies of test files

### Fixed

- Import errors blocking test execution
- Duplicate fixture definitions across test files
- Missing dependency declarations
- Inconsistent test patterns and assertions

## [0.1.0] - 2025-01-01

### Added

- Initial release of Curriculum Repository System
- Core content management functionality
- Basic user authentication and authorization
- Assessment creation and grading
- Learning analytics tracking
- Documentation generation framework

### Known Issues

- Some external dependencies may require manual installation
- Docker configuration may need customization for production use
- Performance optimizations needed for large-scale deployments

---

## Contributing

When contributing to this project, please update the changelog with your changes. Follow the format above and categorize changes appropriately.

For more information on contributing, see [CONTRIBUTING.md](CONTRIBUTING.md).

