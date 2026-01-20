# Test Suite for Book Finder Application

This directory contains comprehensive unit and integration tests for the Book Finder application.

## Test Structure

```
tests/
├── __init__.py                # Test package initialization
├── conftest.py                # Pytest fixtures and configuration
├── test_app.py                # Application initialization tests
├── test_models.py             # Data model unit tests
├── test_routes.py             # Route integration tests
├── test_utils.py              # Utility module unit tests
└── README.md                  # This file
```

## Test Coverage

### Models (`test_models.py`)
- **Book Model**: Initialization, serialization, validation
- **Store Model**: Initialization, Flask-Login interface, GeoJSON location
- **Inventory Model**: Stock tracking, timestamps
- **SearchIndex Model**: Text tokenization, search indexing

### Utilities (`test_utils.py`)
- **SecurityValidator**: Input sanitization, password validation, email/ISBN validation, coordinate validation
- **LoginAttemptTracker**: Failed login tracking, account lockout, attempt cleanup
- **DatabaseManager**: Singleton pattern, database connections

### Routes (`test_routes.py`)
- **Main Routes**: Index page loading
- **Store Routes**: Login, registration, authentication, duplicate handling
- **Book Routes**: Adding books, editing inventory (requires authentication)
- **Search Routes**: ISBN search, title search, location-based search

### Application (`test_app.py`)
- **App Initialization**: Configuration loading, blueprint registration
- **Security**: CSRF protection, session cookies, security headers
- **Routes**: Route registration and basic functionality

## Running Tests

### Run All Tests

```bash
make test
```

Or directly with pytest:

```bash
uv run pytest
```

### Run Specific Test Files

```bash
# Run only model tests
uv run pytest tests/test_models.py

# Run only utility tests
uv run pytest tests/test_utils.py

# Run only route tests
uv run pytest tests/test_routes.py

# Run only app tests
uv run pytest tests/test_app.py
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
uv run pytest tests/test_models.py::TestBookModel

# Run a specific test method
uv run pytest tests/test_models.py::TestBookModel::test_book_initialization
```

### Verbose Output

```bash
# Show detailed test output
uv run pytest -v

# Show test output with detailed failure information
uv run pytest -vv
```

### Code Coverage

```bash
# Run tests with coverage report
uv run pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Fixtures

The `conftest.py` file provides reusable fixtures:

- `app`: Flask application instance with testing configuration
- `client`: Test client for making HTTP requests
- `mock_db`: Mocked database manager
- `sample_book_data`: Sample book dictionary
- `sample_store_data`: Sample store dictionary
- `sample_inventory_data`: Sample inventory dictionary
- `sample_search_index_data`: Sample search index dictionary
- `mock_store`: Mock Store object
- `mock_book`: Mock Book object
- `mock_inventory`: Mock Inventory object
- `authenticated_client`: Test client with logged-in store

## Testing Best Practices

### Unit Tests
- Test individual components in isolation
- Mock external dependencies (database, APIs, etc.)
- Focus on one behavior per test
- Use descriptive test names

### Integration Tests
- Test how components work together
- Mock external services (MongoDB, geocoding APIs)
- Test realistic user scenarios
- Verify HTTP responses and redirects

### Test Organization
- Group related tests in classes
- Use clear docstrings
- Follow AAA pattern: Arrange, Act, Assert
- Keep tests focused and fast

## Mocking

The test suite uses `unittest.mock` for mocking:

```python
from unittest.mock import MagicMock, patch

# Mock database calls
@patch("app.routes.store_routes.db_manager")
def test_with_mocked_db(mock_db, client):
    mock_db.stores.find_one.return_value = None
    # ... test code
```

## Known Test Limitations

1. **Database Dependency**: Some tests require MongoDB mocking
2. **Rate Limiting**: Tests may encounter rate limits in integration tests
3. **External APIs**: Geocoding and other external services are mocked
4. **Background Jobs**: Background tasks are not tested in the current suite

## Continuous Integration

To run tests in CI/CD:

```bash
# Ensure dependencies are installed
uv pip install -e ".[dev]"

# Lint code
make lint

# Format code
make format

# Run tests
make test
```

## Adding New Tests

When adding new features, follow these steps:

1. Write tests first (TDD approach)
2. Add unit tests for new models/utilities in appropriate files
3. Add integration tests for new routes
4. Run tests locally before committing
5. Ensure code coverage remains high

## Debugging Failing Tests

```bash
# Run tests with pdb debugger on failure
uv run pytest --pdb

# Show local variables in tracebacks
uv run pytest -l

# Stop at first failure
uv run pytest -x

# Show captured output even for passing tests
uv run pytest -s
```

## Test Configuration

Test configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

## Environment Variables for Testing

Tests use the `testing` configuration from `config/config.py`:

- `TESTING = True`
- `MONGO_DB_NAME = "bookfinder_test"`
- CSRF protection is disabled
- Debug mode is disabled

## Contributing

When contributing tests:

1. Follow existing test structure and naming conventions
2. Write descriptive test names and docstrings
3. Mock external dependencies appropriately
4. Ensure tests are idempotent (can run multiple times)
5. Run the full test suite before submitting PR
6. Update this README if adding new test categories

## Questions?

For questions about the test suite, refer to:
- Main project [README.md](../README.md)
- Flask testing docs: https://flask.palletsprojects.com/en/latest/testing/
- Pytest docs: https://docs.pytest.org/
