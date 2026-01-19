"""Database connection and management utilities."""
import os
from typing import Optional
from pymongo import MongoClient, GEOSPHERE
from pymongo.database import Database
from pymongo.collection import Collection


class DatabaseManager:
    """Manages MongoDB database connections and collections."""

    _instance: Optional["DatabaseManager"] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        """Singleton pattern to ensure only one database connection."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize database manager."""
        if not hasattr(self, "initialized"):
            self.initialized = True

    def connect(self, uri: Optional[str] = None, db_name: Optional[str] = None) -> None:
        """Connect to MongoDB database.

        Args:
            uri: MongoDB connection URI (defaults to MONGO_URI env var)
            db_name: Database name (defaults to MONGO_DB_NAME env var)
        """
        if self._client is None:
            uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = db_name or os.getenv("MONGO_DB_NAME", "bookfinder")

            self._client = MongoClient(uri)
            self._db = self._client[db_name]

            # Create indexes
            self._create_indexes()

    def _create_indexes(self) -> None:
        """Create necessary database indexes for optimal performance."""
        if self._db is None:
            return

        # Store collection indexes
        stores = self._db.stores
        stores.create_index([("location", GEOSPHERE)])  # Geospatial index for location queries
        stores.create_index("email", unique=True, sparse=True)  # Unique email for authentication

        # Book collection indexes
        books = self._db.books
        books.create_index("isbn", unique=True)  # ISBN is unique identifier

        # Inventory collection indexes
        inventory = self._db.inventory
        inventory.create_index([("store_id", 1), ("isbn", 1)], unique=True)  # Composite key
        inventory.create_index("isbn")  # For book lookup
        inventory.create_index("store_id")  # For store lookup

        # Search index collection indexes
        search_index = self._db.search_index
        search_index.create_index("isbn", unique=True)
        search_index.create_index("title_tokens")
        search_index.create_index("author_tokens")

        # Login attempts collection indexes
        login_attempts = self._db.login_attempts
        login_attempts.create_index([("email", 1), ("timestamp", -1)])
        login_attempts.create_index("timestamp", expireAfterSeconds=2592000)  # Auto-delete after 30 days

    def get_database(self) -> Database:
        """Get the database instance.

        Returns:
            MongoDB Database instance

        Raises:
            RuntimeError: If database is not connected
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db

    def get_collection(self, name: str) -> Collection:
        """Get a collection from the database.

        Args:
            name: Collection name

        Returns:
            MongoDB Collection instance
        """
        return self.get_database()[name]

    @property
    def stores(self) -> Collection:
        """Get stores collection."""
        return self.get_collection("stores")

    @property
    def books(self) -> Collection:
        """Get books collection."""
        return self.get_collection("books")

    @property
    def inventory(self) -> Collection:
        """Get inventory collection."""
        return self.get_collection("inventory")

    @property
    def search_index(self) -> Collection:
        """Get search_index collection."""
        return self.get_collection("search_index")

    @property
    def login_attempts(self) -> Collection:
        """Get login_attempts collection."""
        return self.get_collection("login_attempts")

    def close(self) -> None:
        """Close the database connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global database manager instance
db_manager = DatabaseManager()
