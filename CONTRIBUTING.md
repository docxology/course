# Contributing to Curriculum Repository System

Thank you for your interest in contributing to the Curriculum Repository System! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- A code editor (VS Code, PyCharm, etc.)
- Basic understanding of FastAPI, Pydantic, and pytest

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/curriculum-repository/course.git
   cd course
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

5. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Branching Strategy

- **main**: Production-ready code
- **develop**: Development branch for new features
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Critical bug fixes for production

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the code style guidelines
   - Write tests for new functionality
   - Update documentation as needed

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

4. **Check code quality:**
   ```bash
   make lint
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

6. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style Guidelines

- **Line length**: 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Type hints**: Required for all functions and methods
- **Docstrings**: Required for all public functions and classes
- **Imports**: Group by standard library, third-party, local

### Testing Requirements

- **Unit tests**: Required for all new functions and classes
- **Integration tests**: Required for new services and API endpoints
- **Test coverage**: Minimum 80% overall coverage
- **Test markers**: Use appropriate pytest markers (@pytest.mark.unit, @pytest.mark.integration, etc.)

### Documentation

- Update README.md for significant changes
- Add docstrings to all public APIs
- Update API documentation for new endpoints
- Add changelog entries for user-facing changes

## Pull Request Process

1. **Create a pull request** targeting the `develop` branch
2. **Provide a clear description** of the changes
3. **Reference related issues** if applicable
4. **Ensure all tests pass** in CI
5. **Address reviewer feedback** promptly
6. **Merge will be handled** by maintainers

## Code Review Guidelines

### For Reviewers

- Be respectful and constructive
- Focus on code quality, not personal preference
- Test the changes locally if possible
- Ask questions rather than making assumptions

### For Contributors

- Be open to feedback
- Provide context for your changes
- Respond to questions promptly
- Make requested changes

## Issue Reporting

### Bug Reports

- Use the bug report template
- Include steps to reproduce
- Provide expected vs actual behavior
- Include error messages and stack traces
- Specify environment details (Python version, OS, etc.)

### Feature Requests

- Use the feature request template
- Explain the use case and problem being solved
- Provide examples of how the feature would be used
- Consider edge cases and error scenarios

## Security

- Report security vulnerabilities to security@curriculum-repository.com
- Do not create public issues for security vulnerabilities
- Follow responsible disclosure practices

## Community Guidelines

- Be respectful and inclusive
- Help other contributors
- Follow the code of conduct
- Focus on the technical merits of contributions

## Getting Help

- Check the documentation first
- Search existing issues for similar problems
- Ask questions in discussions
- Join the community chat

---

Thank you for contributing to the Curriculum Repository System! Your contributions help make educational content management better for everyone.

