# Test Suite Documentation

**Comprehensive Testing Strategy for Curriculum Repository System**

## Overview

This test suite provides comprehensive coverage for the Curriculum Repository System with multiple testing layers:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Speed and resource usage testing
- **Edge Case Tests**: Error conditions and boundary testing
- **Documentation Tests**: Feature validation testing

## Test Categories

### 🧪 Unit Tests (`test_*_unit.py`)
- Individual class and function testing
- Mock dependencies for isolation
- Fast execution for development feedback

### 🔗 Integration Tests (`test_*_integration.py`)
- Component interaction testing
- Database integration testing
- External service integration testing

### ⚡ Performance Tests (`test_*_performance.py`)
- Speed and resource usage testing
- Load testing capabilities
- Memory usage monitoring

### 🎯 Edge Case Tests (`test_*_edge_cases.py`)
- Error condition testing
- Boundary value testing
- Invalid input handling

### 📚 Documentation Tests (`test_*_docs.py`)
- Feature validation testing
- Output format verification
- Documentation accuracy testing

## Test File Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Shared fixtures and configuration
├── __init__.py
│
├── test_documentation.py        # Main documentation system tests
├── test_documentation_unit.py   # Documentation unit tests
├── test_documentation_integration.py  # Documentation integration tests
├── test_documentation_performance.py  # Documentation performance tests
├── test_documentation_edge_cases.py   # Documentation edge cases
│
├── test_core_unit.py           # Core models unit tests
├── test_core_integration.py    # Core integration tests
├── test_core_performance.py    # Core performance tests
├── test_core_edge_cases.py     # Core edge cases
│
├── test_content_unit.py        # Content management unit tests
├── test_content_integration.py # Content integration tests
├── test_content_performance.py # Content performance tests
├── test_content_edge_cases.py  # Content edge cases
│
└── [Additional test files for other modules...]
```

## Running Tests

### All Tests
```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```

### Specific Test Category
```bash
# Unit tests only
PYTHONPATH=src python3 -m pytest tests/ -k "unit" -v

# Integration tests only
PYTHONPATH=src python3 -m pytest tests/ -k "integration" -v

# Performance tests only
PYTHONPATH=src python3 -m pytest tests/ -k "performance" -v
```

### Single Test File
```bash
PYTHONPATH=src python3 -m pytest tests/test_documentation_unit.py -v
```

### With Coverage
```bash
PYTHONPATH=src python3 -m pytest tests/ --cov=src/curriculum --cov-report=html
```

## Test Fixtures

### Common Fixtures (conftest.py)
- `sample_user()` - Test user data
- `sample_content()` - Test content data
- `sample_assessment()` - Test assessment data
- `mock_llm_service()` - Mock LLM service for testing
- `temp_output_dir()` - Temporary output directory

### Documentation-Specific Fixtures
- `doc_service()` - Documentation generator service
- `sample_python_file()` - Sample Python file for testing
- `mock_ollama_response()` - Mock LLM responses

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

### CI/CD Integration
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          PYTHONPATH=src python -m pytest tests/ --cov=src/curriculum --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

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
# Run tests for a specific module
PYTHONPATH=src python -m pytest tests/test_content_*.py -v

# Run tests with specific markers
PYTHONPATH=src python -m pytest tests/ -m "unit" -v

# Run tests excluding slow ones
PYTHONPATH=src python -m pytest tests/ -m "not slow" -v
```

### Debugging Tests
```bash
# Run with detailed output
PYTHONPATH=src python -m pytest tests/test_documentation.py::TestDocumentationGenerator::test_basic_functionality -v -s

# Debug with pdb
PYTHONPATH=src python -m pytest tests/test_documentation.py --pdb
```

---

**Last Updated:** October 1, 2025
**Test Coverage Goal:** 85%+
**Test Categories:** 5 (Unit, Integration, Performance, Edge Cases, Documentation)

