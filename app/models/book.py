"""Book model for book data."""
from typing import Optional, Dict, Any
from bson import ObjectId


class Book:
    """Represents a book with ISBN and metadata."""

    def __init__(
        self,
        isbn: str,
        title: str,
        author: str,
        cover_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        _id: Optional[ObjectId] = None,
    ):
        """Initialize a Book instance.

        Args:
            isbn: International Standard Book Number
            title: Book title
            author: Book author(s)
            cover_url: URL to book cover image
            metadata: Additional book metadata (publisher, year, description, etc.)
            _id: MongoDB ObjectId
        """
        self._id = _id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.cover_url = cover_url
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert Book instance to dictionary for MongoDB storage.

        Returns:
            Dictionary representation of the book
        """
        data = {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "metadata": self.metadata,
        }

        if self._id:
            data["_id"] = self._id
        if self.cover_url:
            data["cover_url"] = self.cover_url

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Book":
        """Create a Book instance from a dictionary.

        Args:
            data: Dictionary containing book data

        Returns:
            Book instance
        """
        return cls(
            _id=data.get("_id"),
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            cover_url=data.get("cover_url"),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation of Book."""
        return f"<Book '{self.title}' by {self.author} (ISBN: {self.isbn})>"
