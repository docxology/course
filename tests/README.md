# Test Suite Documentation

**Comprehensive Testing Strategy for Curriculum Repository System**

## Overview

## Test Suites

| Suite | Coverage and example files |
| --- | --- |
| [Unit](unit/) | Local component and workflow checks, including [core models](unit/test_core_models.py) and [content workflow quality](unit/test_content_workflow_quality.py). |
| [Integration](integration/) | Component interactions, database, CLI, and route tests, including the [content service](integration/test_content_content_service.py). |
| [Performance](performance/) | [Documentation generation benchmarks](performance/test_documentation_performance.py). |
| [Security](security/) | Authentication and token validation checks. |

The documentation service's [main tests](integration/test_documentation.py),
[unit tests](integration/test_documentation_unit.py),
[integration tests](integration/test_documentation_integration.py),
[comprehensive tests](integration/test_documentation_comprehensive.py), and
[edge cases](integration/test_documentation_edge_cases.py) all live in
`tests/integration/`. The unit marker applies to some tests in that directory.

## Running Tests

Install the locked development dependencies with the [quickstart](../docs/quickstart.md)
and run the commands below from the repository root. Read the integration
fixtures before running tests that use additional services.

### All Tests
```bash
uv run --no-sync pytest tests/ -v
```

### Specific Suite
```bash
# Offline unit suite
uv run --no-sync pytest tests/unit --no-cov

# Integration suite
uv run --no-sync pytest tests/integration --no-cov -v

# Documentation benchmarks
uv run --no-sync pytest tests/performance --no-cov -v
```

### Single Test File
```bash
uv run --no-sync pytest tests/integration/test_documentation_unit.py --no-cov -v
```

### With Coverage

The default configuration in [pyproject.toml](../pyproject.toml) measures
coverage over `src/` and produces terminal, HTML, and XML reports. Use
`--no-cov` for focused runs that do not need reports.

## Test Fixtures

### Common Fixtures

[conftest.py](conftest.py) defines shared data and service fixtures.

- `sample_user()` - Test user data
- `sample_content()` - Test content data
- `sample_assessment()` - Test assessment data

### Documentation-Specific Fixtures

[test_documentation.py](integration/test_documentation.py) defines
`doc_service` and `sample_python_file`. The shared
`offline_documentation_provider` fixture simulates an unavailable Ollama
provider for the documentation test files.

## Test Patterns

### Unit Test Pattern
```python
class TestComponentName:
    """Unit tests for ComponentName."""

    def test_basic_functionality(self, fixture_name):
        """Test basic component functionality."""
        # Arrange
        component = ComponentName()

        # Act
        result = component.method()

        # Assert
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            ComponentName().invalid_method()
```

### Integration Test Pattern
```python
class TestComponentIntegration:
    """Integration tests for component interactions."""

    def test_component_interaction(self, component_a, component_b):
        """Test interaction between two components."""
        # Arrange
        component_a.setup()
        component_b.setup()

        # Act
        result = component_a.process(component_b.data())

        # Assert
        assert result.is_valid()
```

### Performance Test Pattern
```python
class TestComponentPerformance:
    """Performance tests for component speed and resource usage."""

    def test_method_performance(self, benchmark):
        """Test method performance under load."""
        # Arrange
        component = ComponentName()

        # Act & Assert
        result = benchmark(component.method, large_dataset)
        assert result.execution_time < 0.1  # Less than 100ms
```

## Test Data Management

### Sample Data Creation
```python
def create_sample_user(user_id: str = "user123") -> User:
    """Create sample user for testing."""
    return User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        role=UserRole.STUDENT
    )
```

### Test Data Cleanup
```python
@pytest.fixture
def cleanup_test_data():
    """Clean up test data after tests."""
    yield
    # Cleanup code here
    TestDataManager.cleanup()
```

## Mocking Strategy

### External Service Mocking
```python
@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    with patch('curriculum.documentation.generator.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "Mock LLM response"
        }
        yield mock_post
```

### Database Mocking
```python
@pytest.fixture
def mock_database():
    """Mock database operations."""
    with patch('curriculum.db.base.DatabaseInterface') as mock_db:
        mock_db.return_value.query.return_value = []
        yield mock_db
```

## Performance Testing

### Benchmarking
```python
def test_documentation_generation_performance(benchmark):
    """Benchmark documentation generation speed."""
    doc_service = DocumentationGeneratorService()

    # Benchmark the generation process
    result = benchmark(
        doc_service.generate_documentation,
        package_path="src/curriculum/core",
        use_llm=False
    )

    assert result["status"] == "success"
    assert benchmark.stats["mean"] < 5.0  # Less than 5 seconds
```

### Memory Usage Testing
```python
def test_memory_usage():
    """Test memory usage during documentation generation."""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Run memory-intensive operation
    doc_service = DocumentationGeneratorService()
    doc_service.generate_documentation(package_path="src/curriculum")

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    assert memory_increase < 100  # Less than 100MB increase
```

## Edge Case Testing

### Invalid Input Testing
```python
def test_invalid_file_path():
    """Test handling of invalid file paths."""
    doc_service = DocumentationGeneratorService()

    with pytest.raises(FileNotFoundError):
        doc_service.generate_documentation(package_path="/nonexistent/path")
```

### Boundary Value Testing
```python
def test_empty_package():
    """Test handling of empty packages."""
    doc_service = DocumentationGeneratorService()

    # Create empty test package
    empty_package = Path("tests/test_data/empty_package")
    empty_package.mkdir(exist_ok=True)
    (empty_package / "__init__.py").write_text("")

    result = doc_service.generate_documentation(package_path=str(empty_package))

    assert result["status"] == "success"
    assert result["modules_documented"] == 0
```

## Test Documentation

Each test file should include:
- **Module docstring** explaining test purpose
- **Class docstrings** for test categories
- **Method docstrings** explaining what each test validates
- **Comments** for complex test logic

## Continuous Integration

The [CI workflow](../.github/workflows/ci.yml) installs locked dependencies and
runs pytest by marker across its supported Python matrix. The
[performance workflow](../.github/workflows/performance.yml) times the
documentation benchmarks.

## Test Maintenance

### Regular Updates
- **Review test coverage** monthly
- **Update test data** when models change
- **Add new tests** for new features
- **Remove obsolete tests** during refactoring

### Test Data Management
- **Sample data** should be realistic but not sensitive
- **Test databases** should be isolated
- **Mock data** should match production data structure

## Getting Help

### Running Specific Tests
```bash
# Run content workflow tests
uv run --no-sync pytest tests/unit/test_content_workflow_quality.py --no-cov -v

# Select tests by marker within the integration suite
uv run --no-sync pytest tests/integration -m integration --no-cov -v

# Exclude slow integration tests
uv run --no-sync pytest tests/integration -m "not slow" --no-cov -v
```

### Debugging Tests
```bash
# Run with detailed output
uv run --no-sync pytest tests/integration/test_documentation.py::TestDocumentationGenerator::test_initialization --no-cov -v -s

# Debug with pdb
uv run --no-sync pytest tests/integration/test_documentation.py --no-cov --pdb
```
