"""Store model for bookstore data."""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId


class Store:
    """Represents a bookstore with location and contact information."""

    def __init__(
        self,
        name: str,
        store_type: str,
        latitude: float,
        longitude: float,
        address: str,
        hours: str,
        contact: str,
        website: Optional[str] = None,
        encoded_store_photo: Optional[str] = None,
        password_hash: Optional[str] = None,
        email: Optional[str] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
    ):
        """Initialize a Store instance.

        Args:
            name: Store name
            store_type: Type of store (e.g., 'bookstore', 'library', 'thrift')
            latitude: Geographic latitude
            longitude: Geographic longitude
            address: Physical address
            hours: Business hours
            contact: Contact phone number
            website: Store website URL
            encoded_store_photo: Base64 encoded store photo
            password_hash: Hashed password for store login
            email: Store email for login
            _id: MongoDB ObjectId
            created_at: Creation timestamp
        """
        self._id = _id
        self.name = name
        self.store_type = store_type
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.hours = hours
        self.contact = contact
        self.website = website
        self.encoded_store_photo = encoded_store_photo
        self.password_hash = password_hash
        self.email = email
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert Store instance to dictionary for MongoDB storage.

        Returns:
            Dictionary representation of the store
        """
        data = {
            "name": self.name,
            "type": self.store_type,
            "location": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude]  # GeoJSON format [lng, lat]
            },
            "address": self.address,
            "hours": self.hours,
            "contact": self.contact,
            "created_at": self.created_at,
        }

        if self._id:
            data["_id"] = self._id
        if self.website:
            data["website"] = self.website
        if self.encoded_store_photo:
            data["encoded_store_photo"] = self.encoded_store_photo
        if self.password_hash:
            data["password_hash"] = self.password_hash
        if self.email:
            data["email"] = self.email

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Store":
        """Create a Store instance from a dictionary.

        Args:
            data: Dictionary containing store data

        Returns:
            Store instance
        """
        location = data.get("location", {})
        coordinates = location.get("coordinates", [0, 0])

        return cls(
            _id=data.get("_id"),
            name=data["name"],
            store_type=data.get("type", "bookstore"),
            latitude=coordinates[1],  # GeoJSON is [lng, lat]
            longitude=coordinates[0],
            address=data["address"],
            hours=data["hours"],
            contact=data["contact"],
            website=data.get("website"),
            encoded_store_photo=data.get("encoded_store_photo"),
            password_hash=data.get("password_hash"),
            email=data.get("email"),
            created_at=data.get("created_at"),
        )

    # Flask-Login required methods
    @property
    def is_authenticated(self) -> bool:
        """Return True if the user is authenticated."""
        return True

    @property
    def is_active(self) -> bool:
        """Return True if this is an active user."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Return False as stores are not anonymous users."""
        return False

    def get_id(self) -> str:
        """Return the user ID as a string."""
        return str(self._id) if self._id else None

    def __repr__(self) -> str:
        """String representation of Store."""
        return f"<Store {self.name} ({self.store_type})>"
