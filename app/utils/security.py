"""Security utilities for input validation and sanitization."""

import re
from typing import Any

from email_validator import EmailNotValidError, validate_email


class SecurityValidator:
    """Provides security validation and sanitization methods."""

    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    # NoSQL injection patterns to detect
    NOSQL_INJECTION_PATTERNS = [
        r"\$where",
        r"\$ne",
        r"\$gt",
        r"\$gte",
        r"\$lt",
        r"\$lte",
        r"\$in",
        r"\$nin",
        r"\$regex",
        r"\$exists",
        r"\$type",
        r"\$expr",
        r"\$jsonSchema",
        r"\$mod",
        r"\$text",
        r"\$elemMatch",
    ]

    @staticmethod
    def sanitize_input(value: Any) -> Any:
        """Sanitize input to prevent NoSQL injection attacks.

        This prevents MongoDB operator injection by rejecting any string
        that contains MongoDB operators or converting dicts to safe strings.

        Args:
            value: Input value to sanitize

        Returns:
            Sanitized value

        Raises:
            ValueError: If input contains potential injection patterns
        """
        # If it's None, return as is
        if value is None:
            return value

        # If it's a dict or list, reject it (prevent object injection)
        if isinstance(value, (dict, list)):
            raise ValueError("Complex types not allowed in user input")

        # Convert to string
        str_value = str(value)

        # Check for MongoDB operators
        for pattern in SecurityValidator.NOSQL_INJECTION_PATTERNS:
            if re.search(pattern, str_value, re.IGNORECASE):
                raise ValueError(f"Potentially dangerous pattern detected: {pattern}")

        return str_value

    @staticmethod
    def sanitize_query_dict(query: dict[str, Any]) -> dict[str, Any]:
        """Sanitize a query dictionary to prevent NoSQL injection.

        Args:
            query: Query dictionary to sanitize

        Returns:
            Sanitized query dictionary
        """
        sanitized = {}
        for key, value in query.items():
            # Sanitize the key to prevent operator injection
            if key.startswith("$"):
                raise ValueError(f"MongoDB operators not allowed in keys: {key}")

            # Sanitize the value
            if isinstance(value, str):
                sanitized[key] = SecurityValidator.sanitize_input(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif value is None:
                sanitized[key] = None
            else:
                raise ValueError(f"Unsupported type for query value: {type(value)}")

        return sanitized

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str | None]:
        """Validate password meets security requirements.

        Password must:
        - Be at least 8 characters long
        - Contain at least one uppercase letter
        - Contain at least one lowercase letter
        - Contain at least one digit
        - Contain at least one special character

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        if len(password) < SecurityValidator.MIN_PASSWORD_LENGTH:
            return (
                False,
                f"Password must be at least {SecurityValidator.MIN_PASSWORD_LENGTH} characters long",
            )

        if len(password) > SecurityValidator.MAX_PASSWORD_LENGTH:
            return (
                False,
                f"Password must not exceed {SecurityValidator.MAX_PASSWORD_LENGTH} characters",
            )

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "Password must contain at least one special character"

        # Check for common passwords (basic check)
        common_passwords = [
            "password",
            "password123",
            "12345678",
            "qwerty",
            "abc123",
            "monkey",
            "1234567890",
            "letmein",
            "trustno1",
            "dragon",
            "baseball",
            "iloveyou",
            "master",
            "sunshine",
            "ashley",
            "bailey",
            "passw0rd",
            "shadow",
            "123123",
            "654321",
        ]
        if password.lower() in common_passwords:
            return False, "Password is too common. Please choose a stronger password"

        return True, None

    @staticmethod
    def validate_email_address(email: str) -> tuple[bool, str | None]:
        """Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message or normalized_email)
        """
        if not email:
            return False, "Email is required"

        try:
            # Validate and normalize email
            valid = validate_email(email, check_deliverability=False)
            return True, valid.normalized
        except EmailNotValidError as e:
            return False, str(e)

    @staticmethod
    def validate_isbn(isbn: str) -> tuple[bool, str | None]:
        """Validate ISBN format (ISBN-10 or ISBN-13).

        Args:
            isbn: ISBN to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isbn:
            return False, "ISBN is required"

        # Remove hyphens and spaces
        clean_isbn = re.sub(r"[\s-]", "", isbn)

        # Check if it's a valid ISBN-10 or ISBN-13
        if len(clean_isbn) == 10:
            # ISBN-10 validation
            if not re.match(r"^\d{9}[\dX]$", clean_isbn, re.IGNORECASE):
                return False, "Invalid ISBN-10 format"
        elif len(clean_isbn) == 13:
            # ISBN-13 validation
            if not re.match(r"^\d{13}$", clean_isbn):
                return False, "Invalid ISBN-13 format"
        else:
            return False, "ISBN must be 10 or 13 characters"

        return True, None

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize a string input by trimming and limiting length.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string

        Raises:
            ValueError: If string is too long
        """
        if not isinstance(value, str):
            value = str(value)

        # Trim whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            raise ValueError(f"Input too long (max {max_length} characters)")

        return value

    @staticmethod
    def validate_latitude(lat: float) -> tuple[bool, str | None]:
        """Validate latitude value.

        Args:
            lat: Latitude to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            lat_float = float(lat)
            if -90 <= lat_float <= 90:
                return True, None
            return False, "Latitude must be between -90 and 90"
        except (ValueError, TypeError):
            return False, "Invalid latitude format"

    @staticmethod
    def validate_longitude(lng: float) -> tuple[bool, str | None]:
        """Validate longitude value.

        Args:
            lng: Longitude to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            lng_float = float(lng)
            if -180 <= lng_float <= 180:
                return True, None
            return False, "Longitude must be between -180 and 180"
        except (ValueError, TypeError):
            return False, "Invalid longitude format"

    @staticmethod
    def validate_quantity(qty: int) -> tuple[bool, str | None]:
        """Validate quantity value.

        Args:
            qty: Quantity to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            qty_int = int(qty)
            if qty_int < 0:
                return False, "Quantity cannot be negative"
            if qty_int > 1000000:
                return False, "Quantity is unrealistically high"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid quantity format"
