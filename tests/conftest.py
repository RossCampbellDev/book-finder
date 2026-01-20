"""Pytest configuration and fixtures for testing."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from app import create_app


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def mock_db():
    """Create a mock database manager."""
    mock = MagicMock()
    mock.stores = MagicMock()
    mock.books = MagicMock()
    mock.inventory = MagicMock()
    mock.search_index = MagicMock()
    mock.login_attempts = MagicMock()
    return mock


@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
        "_id": ObjectId(),
        "isbn": "978-0-545-01022-1",
        "title": "Harry Potter and the Deathly Hallows",
        "author": "J.K. Rowling",
        "cover_url": "https://example.com/cover.jpg",
        "metadata": {"pages": 607, "publisher": "Scholastic"},
    }


@pytest.fixture
def sample_store_data():
    """Sample store data for testing."""
    return {
        "_id": ObjectId(),
        "name": "The Book Nook",
        "store_type": "bookstore",
        "latitude": 53.4808,
        "longitude": -2.2426,
        "address": "123 Main St, Manchester, M1 1AA",
        "hours": "Mon-Sat: 9am-6pm",
        "contact": "0161-123-4567",
        "website": "https://booknook.com",
        "email": "contact@booknook.com",
        "password_hash": b"$2b$12$AAAAAAAAAAAAAAAAAAAAAA",
        "created_at": datetime.now(UTC),
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    store_id = ObjectId()
    return {
        "_id": ObjectId(),
        "store_id": store_id,
        "isbn": "978-0-545-01022-1",
        "qty": 5,
        "condition": "new",
        "last_updated": datetime.now(UTC),
    }


@pytest.fixture
def sample_search_index_data():
    """Sample search index data for testing."""
    return {
        "_id": ObjectId(),
        "isbn": "978-0-545-01022-1",
        "tokens": ["harry", "potter", "deathly", "hallows", "jk", "rowling"],
    }


@pytest.fixture
def mock_store(sample_store_data):
    """Create a mock Store object."""
    from app.models import Store

    return Store.from_dict(sample_store_data)


@pytest.fixture
def mock_book(sample_book_data):
    """Create a mock Book object."""
    from app.models import Book

    return Book.from_dict(sample_book_data)


@pytest.fixture
def mock_inventory(sample_inventory_data):
    """Create a mock Inventory object."""
    from app.models import Inventory

    return Inventory.from_dict(sample_inventory_data)


@pytest.fixture
def authenticated_client(client, mock_store, monkeypatch):
    """Create an authenticated test client with a logged-in store."""
    from flask_login import login_user

    with client.application.test_request_context():
        login_user(mock_store)
        yield client
