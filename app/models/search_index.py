"""Search index model for efficient book searching."""

from typing import Any

from bson import ObjectId


class SearchIndex:
    """Represents a search index for books with tokenized fields."""

    def __init__(
        self,
        isbn: str,
        title_tokens: list[str],
        author_tokens: list[str],
        _id: ObjectId | None = None,
    ):
        """Initialize a SearchIndex instance.

        Args:
            isbn: Book ISBN (primary key)
            title_tokens: Tokenized title words for searching
            author_tokens: Tokenized author words for searching
            _id: MongoDB ObjectId
        """
        self._id = _id
        self.isbn = isbn
        self.title_tokens = title_tokens
        self.author_tokens = author_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert SearchIndex instance to dictionary for MongoDB storage.

        Returns:
            Dictionary representation of the search index
        """
        data = {
            "isbn": self.isbn,
            "title_tokens": self.title_tokens,
            "author_tokens": self.author_tokens,
        }

        if self._id:
            data["_id"] = self._id

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchIndex":
        """Create a SearchIndex instance from a dictionary.

        Args:
            data: Dictionary containing search index data

        Returns:
            SearchIndex instance
        """
        return cls(
            _id=data.get("_id"),
            isbn=data["isbn"],
            title_tokens=data.get("title_tokens", []),
            author_tokens=data.get("author_tokens", []),
        )

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Tokenize text into searchable words.

        Args:
            text: Text to tokenize

        Returns:
            List of lowercase tokens
        """
        # Simple tokenization: lowercase, split on whitespace, remove punctuation
        import re

        # Remove punctuation and convert to lowercase
        clean_text = re.sub(r"[^\w\s]", "", text.lower())
        # Split into words
        return clean_text.split()

    @classmethod
    def create_from_book(cls, isbn: str, title: str, author: str) -> "SearchIndex":
        """Create a SearchIndex from book information.

        Args:
            isbn: Book ISBN
            title: Book title
            author: Book author

        Returns:
            SearchIndex instance with tokenized fields
        """
        title_tokens = cls.tokenize(title)
        author_tokens = cls.tokenize(author)

        return cls(
            isbn=isbn,
            title_tokens=title_tokens,
            author_tokens=author_tokens,
        )

    def __repr__(self) -> str:
        """String representation of SearchIndex."""
        return f"<SearchIndex ISBN:{self.isbn}>"
