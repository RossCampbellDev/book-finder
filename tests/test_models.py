"""Unit tests for data models."""

from datetime import UTC, datetime

from bson import ObjectId

from app.models import Book, Inventory, SearchIndex, Store


class TestBookModel:
    """Tests for Book model."""

    def test_book_initialization(self):
        """Test Book instance initialization."""
        book = Book(
            isbn="978-0-545-01022-1",
            title="Test Book",
            author="Test Author",
            cover_url="https://example.com/cover.jpg",
        )

        assert book.isbn == "978-0-545-01022-1"
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.cover_url == "https://example.com/cover.jpg"
        assert book.metadata == {}
        assert book._id is None

    def test_book_with_metadata(self):
        """Test Book with metadata."""
        metadata = {"pages": 300, "publisher": "Test Publisher"}
        book = Book(
            isbn="978-0-545-01022-1",
            title="Test Book",
            author="Test Author",
            metadata=metadata,
        )

        assert book.metadata == metadata

    def test_book_to_dict(self):
        """Test Book to_dict method."""
        book = Book(
            isbn="978-0-545-01022-1", title="Test Book", author="Test Author", _id=ObjectId()
        )

        book_dict = book.to_dict()

        assert book_dict["isbn"] == "978-0-545-01022-1"
        assert book_dict["title"] == "Test Book"
        assert book_dict["author"] == "Test Author"
        assert "_id" in book_dict
        assert book_dict["metadata"] == {}

    def test_book_from_dict(self, sample_book_data):
        """Test Book from_dict class method."""
        book = Book.from_dict(sample_book_data)

        assert book.isbn == sample_book_data["isbn"]
        assert book.title == sample_book_data["title"]
        assert book.author == sample_book_data["author"]
        assert book._id == sample_book_data["_id"]

    def test_book_repr(self):
        """Test Book string representation."""
        book = Book(isbn="978-0-545-01022-1", title="Test Book", author="Test Author")

        repr_str = repr(book)

        assert "Book" in repr_str
        assert "978-0-545-01022-1" in repr_str


class TestStoreModel:
    """Tests for Store model."""

    def test_store_initialization(self):
        """Test Store instance initialization."""
        store = Store(
            name="Test Store",
            store_type="bookstore",
            latitude=53.4808,
            longitude=-2.2426,
            address="123 Test St",
            hours="9-5",
            contact="555-1234",
        )

        assert store.name == "Test Store"
        assert store.store_type == "bookstore"
        assert store.latitude == 53.4808
        assert store.longitude == -2.2426
        assert store.address == "123 Test St"
        assert store.hours == "9-5"
        assert store.contact == "555-1234"
        assert store.created_at is not None

    def test_store_with_optional_fields(self):
        """Test Store with optional fields."""
        store = Store(
            name="Test Store",
            store_type="bookstore",
            latitude=53.4808,
            longitude=-2.2426,
            address="123 Test St",
            hours="9-5",
            contact="555-1234",
            website="https://test.com",
            email="test@test.com",
        )

        assert store.website == "https://test.com"
        assert store.email == "test@test.com"

    def test_store_to_dict(self):
        """Test Store to_dict method."""
        store = Store(
            name="Test Store",
            store_type="bookstore",
            latitude=53.4808,
            longitude=-2.2426,
            address="123 Test St",
            hours="9-5",
            contact="555-1234",
            _id=ObjectId(),
        )

        store_dict = store.to_dict()

        assert store_dict["name"] == "Test Store"
        assert store_dict["type"] == "bookstore"  # Note: uses "type" key, not "store_type"
        assert "location" in store_dict
        assert store_dict["location"]["type"] == "Point"
        assert store_dict["location"]["coordinates"] == [-2.2426, 53.4808]

    def test_store_from_dict(self, sample_store_data):
        """Test Store from_dict class method."""
        store = Store.from_dict(sample_store_data)

        assert store.name == sample_store_data["name"]
        assert store.store_type == sample_store_data["store_type"]
        assert store.email == sample_store_data["email"]
        assert store._id == sample_store_data["_id"]

    def test_store_flask_login_interface(self):
        """Test Store implements Flask-Login interface."""
        store = Store(
            name="Test Store",
            store_type="bookstore",
            latitude=53.4808,
            longitude=-2.2426,
            address="123 Test St",
            hours="9-5",
            contact="555-1234",
            _id=ObjectId(),
        )

        # Test Flask-Login required methods
        assert hasattr(store, "is_authenticated")
        assert hasattr(store, "is_active")
        assert hasattr(store, "is_anonymous")
        assert hasattr(store, "get_id")

        assert store.is_authenticated is True
        assert store.is_active is True
        assert store.is_anonymous is False
        assert store.get_id() == str(store._id)

    def test_store_repr(self):
        """Test Store string representation."""
        store = Store(
            name="Test Store",
            store_type="bookstore",
            latitude=53.4808,
            longitude=-2.2426,
            address="123 Test St",
            hours="9-5",
            contact="555-1234",
        )

        repr_str = repr(store)

        assert "Store" in repr_str
        assert "Test Store" in repr_str


class TestInventoryModel:
    """Tests for Inventory model."""

    def test_inventory_initialization(self):
        """Test Inventory instance initialization."""
        store_id = ObjectId()
        inventory = Inventory(store_id=store_id, isbn="978-0-545-01022-1", qty=5, condition="new")

        assert inventory.store_id == store_id
        assert inventory.isbn == "978-0-545-01022-1"
        assert inventory.qty == 5
        assert inventory.condition == "new"
        assert inventory.last_updated is not None

    def test_inventory_with_last_updated(self):
        """Test Inventory with custom last_updated."""
        store_id = ObjectId()
        timestamp = datetime.now(UTC)
        inventory = Inventory(
            store_id=store_id,
            isbn="978-0-545-01022-1",
            qty=5,
            condition="new",
            last_updated=timestamp,
        )

        assert inventory.last_updated == timestamp

    def test_inventory_to_dict(self):
        """Test Inventory to_dict method."""
        store_id = ObjectId()
        inventory = Inventory(
            store_id=store_id, isbn="978-0-545-01022-1", qty=5, condition="new", _id=ObjectId()
        )

        inv_dict = inventory.to_dict()

        assert inv_dict["store_id"] == store_id
        assert inv_dict["isbn"] == "978-0-545-01022-1"
        assert inv_dict["qty"] == 5
        assert inv_dict["condition"] == "new"
        assert "_id" in inv_dict

    def test_inventory_from_dict(self, sample_inventory_data):
        """Test Inventory from_dict class method."""
        inventory = Inventory.from_dict(sample_inventory_data)

        assert inventory.store_id == sample_inventory_data["store_id"]
        assert inventory.isbn == sample_inventory_data["isbn"]
        assert inventory.qty == sample_inventory_data["qty"]
        assert inventory.condition == sample_inventory_data["condition"]

    def test_inventory_repr(self):
        """Test Inventory string representation."""
        store_id = ObjectId()
        inventory = Inventory(store_id=store_id, isbn="978-0-545-01022-1", qty=5, condition="new")

        repr_str = repr(inventory)

        assert "Inventory" in repr_str
        assert "978-0-545-01022-1" in repr_str


class TestSearchIndexModel:
    """Tests for SearchIndex model."""

    def test_search_index_initialization(self):
        """Test SearchIndex instance initialization."""
        index = SearchIndex(
            isbn="978-0-545-01022-1", title_tokens=["harry", "potter"], author_tokens=["rowling"]
        )

        assert index.isbn == "978-0-545-01022-1"
        assert index.title_tokens == ["harry", "potter"]
        assert index.author_tokens == ["rowling"]
        assert index._id is None

    def test_search_index_to_dict(self):
        """Test SearchIndex to_dict method."""
        index = SearchIndex(
            isbn="978-0-545-01022-1",
            title_tokens=["harry", "potter"],
            author_tokens=["rowling"],
            _id=ObjectId(),
        )

        index_dict = index.to_dict()

        assert index_dict["isbn"] == "978-0-545-01022-1"
        assert index_dict["title_tokens"] == ["harry", "potter"]
        assert index_dict["author_tokens"] == ["rowling"]
        assert "_id" in index_dict

    def test_search_index_from_dict(self):
        """Test SearchIndex from_dict class method."""
        data = {
            "_id": ObjectId(),
            "isbn": "978-0-545-01022-1",
            "title_tokens": ["harry", "potter"],
            "author_tokens": ["rowling"],
        }
        index = SearchIndex.from_dict(data)

        assert index.isbn == data["isbn"]
        assert index.title_tokens == data["title_tokens"]
        assert index.author_tokens == data["author_tokens"]
        assert index._id == data["_id"]

    def test_tokenize(self):
        """Test tokenize static method."""
        text = "Harry Potter and the Deathly Hallows"
        tokens = SearchIndex.tokenize(text)

        assert isinstance(tokens, list)
        assert "harry" in tokens
        assert "potter" in tokens
        assert "deathly" in tokens
        assert "hallows" in tokens
        # "and" and "the" should be included
        assert "and" in tokens
        assert "the" in tokens

    def test_tokenize_removes_punctuation(self):
        """Test tokenize removes punctuation."""
        text = "Hello, World! How's it going?"
        tokens = SearchIndex.tokenize(text)

        assert "hello" in tokens
        assert "world" in tokens
        assert "hows" in tokens  # Apostrophe removed
        # Punctuation should be removed
        assert "," not in tokens
        assert "!" not in tokens
        assert "?" not in tokens

    def test_tokenize_empty_string(self):
        """Test tokenize with empty string."""
        tokens = SearchIndex.tokenize("")

        assert tokens == []

    def test_create_from_book(self):
        """Test create_from_book class method."""
        index = SearchIndex.create_from_book(
            isbn="978-0-545-01022-1", title="Test Book", author="Test Author"
        )

        assert index.isbn == "978-0-545-01022-1"
        assert isinstance(index.title_tokens, list)
        assert isinstance(index.author_tokens, list)
        assert "test" in index.title_tokens
        assert "book" in index.title_tokens
        assert "test" in index.author_tokens
        assert "author" in index.author_tokens

    def test_search_index_repr(self):
        """Test SearchIndex string representation."""
        index = SearchIndex(
            isbn="978-0-545-01022-1", title_tokens=["harry", "potter"], author_tokens=["rowling"]
        )

        repr_str = repr(index)

        assert "SearchIndex" in repr_str
        assert "978-0-545-01022-1" in repr_str
