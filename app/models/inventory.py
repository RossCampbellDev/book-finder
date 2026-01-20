"""Inventory model for tracking book stock at stores."""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId


class Inventory:
    """Represents inventory of a book at a specific store."""

    def __init__(
        self,
        store_id: ObjectId,
        isbn: str,
        qty: int,
        condition: str,
        last_updated: datetime | None = None,
        _id: ObjectId | None = None,
    ):
        """Initialize an Inventory instance.

        Args:
            store_id: Reference to Store ObjectId
            isbn: Book ISBN
            qty: Quantity in stock
            condition: Condition of the book (e.g., 'new', 'used-like-new', 'used-good', 'used-fair')
            last_updated: Last update timestamp
            _id: MongoDB ObjectId
        """
        self._id = _id
        self.store_id = store_id
        self.isbn = isbn
        self.qty = qty
        self.condition = condition
        self.last_updated = last_updated or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert Inventory instance to dictionary for MongoDB storage.

        Returns:
            Dictionary representation of the inventory item
        """
        data = {
            "store_id": self.store_id,
            "isbn": self.isbn,
            "qty": self.qty,
            "condition": self.condition,
            "last_updated": self.last_updated,
        }

        if self._id:
            data["_id"] = self._id

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Inventory":
        """Create an Inventory instance from a dictionary.

        Args:
            data: Dictionary containing inventory data

        Returns:
            Inventory instance
        """
        return cls(
            _id=data.get("_id"),
            store_id=data["store_id"],
            isbn=data["isbn"],
            qty=data["qty"],
            condition=data["condition"],
            last_updated=data.get("last_updated", datetime.now(UTC)),
        )

    def __repr__(self) -> str:
        """String representation of Inventory."""
        return f"<Inventory ISBN:{self.isbn} Store:{self.store_id} Qty:{self.qty}>"
