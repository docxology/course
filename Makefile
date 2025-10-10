.PHONY: help install install-dev test test-fast test-unit test-integration test-slow test-coverage lint lint-fix format type-check clean docs docker-up docker-down docker-logs docker-build pre-commit security-scan help

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-fast     - Run only fast tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-slow     - Run slow tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint          - Run linting (black, flake8, mypy, isort)"
	@echo "  lint-fix      - Fix linting issues automatically"
	@echo "  format        - Format code with black and isort"
	@echo "  type-check    - Run mypy type checking"
	@echo "  clean         - Clean build artifacts and cache"
	@echo "  docs          - Generate documentation"
	@echo "  docker-up     - Start Docker containers"
	@echo "  docker-down   - Stop Docker containers"
	@echo "  docker-logs   - View Docker logs"
	@echo "  docker-build  - Build Docker image"
	@echo "  pre-commit    - Run pre-commit hooks"
	@echo "  security-scan - Run security scan"
	@echo "  help          - Show this help message"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Testing
test:
	PYTHONPATH=src python -m pytest tests/ -v --tb=short

test-fast:
	PYTHONPATH=src python -m pytest tests/ -m "not slow" -v --tb=short

test-unit:
	PYTHONPATH=src python -m pytest tests/ -m unit -v --tb=short

test-integration:
	PYTHONPATH=src python -m pytest tests/ -m integration -v --tb=short

test-slow:
	PYTHONPATH=src python -m pytest tests/ -m slow -v --tb=short

test-coverage:
	PYTHONPATH=src python -m pytest tests/ --cov=src --cov-report=html --cov-report=xml --cov-report=term-missing

# Code quality
lint:
	black --check src/ tests/
	flake8 src/ tests/
	mypy src/
	isort --check-only src/ tests/

lint-fix:
	black src/ tests/
	isort src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

# Cleaning
clean:
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -delete
	find . -type d -name ".mypy_cache" -delete
	rm -f coverage.xml
	rm -rf dist/
	rm -rf build/

# Documentation
docs:
	# Generate documentation with LLM analysis
	PYTHONPATH=src python -c "
	from curriculum.documentation import DocumentationGeneratorService
	import tempfile
	import json

	with tempfile.TemporaryDirectory() as tmp_dir:
		doc_service = DocumentationGeneratorService(output_dir=tmp_dir)
		result = doc_service.generate_documentation(
			package_path='src/curriculum',
			use_llm=False
		)
		print(f'Documentation generated: {result}')
	"

	# Build MkDocs documentation
	mkdocs build --clean

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker build -t curriculum-repository .

# Development tools
pre-commit:
	pre-commit run --all-files

security-scan:
	# Install security tools
	pip install safety bandit[toml] pip-audit

	# Run security scans
	safety check --json --output safety-report.json || true
	bandit -r src/ -f json -o bandit-report.json || true
	pip-audit --format=json --output pip-audit-report.json || true

	@echo "Security scan completed. Check reports in:"
	@echo "  - safety-report.json"
	@echo "  - bandit-report.json"
	@echo "  - pip-audit-report.json"

