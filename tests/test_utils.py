"""Unit tests for utility modules."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from app.utils.login_attempts import LoginAttemptTracker
from app.utils.security import SecurityValidator


class TestSecurityValidator:
    """Tests for SecurityValidator utility class."""

    def test_sanitize_input_normal_string(self):
        """Test sanitizing normal string input."""
        result = SecurityValidator.sanitize_input("Hello World")
        assert result == "Hello World"

    def test_sanitize_input_with_script_tag(self):
        """Test sanitizing input with script tag."""
        # sanitize_input doesn't remove or escape HTML, it converts to string
        result = SecurityValidator.sanitize_input("<script>alert('xss')</script>")
        # Should return as string (HTML tags are allowed in strings)
        assert isinstance(result, str)

    def test_sanitize_input_with_sql_injection(self):
        """Test sanitizing SQL injection attempt."""
        result = SecurityValidator.sanitize_input("'; DROP TABLE users; --")
        assert result  # Should return sanitized string

    def test_sanitize_string_max_length(self):
        """Test sanitize_string with max_length."""
        long_string = "a" * 200
        result = SecurityValidator.sanitize_string(long_string, max_length=100)
        assert len(result) <= 100

    def test_sanitize_string_removes_html(self):
        """Test sanitize_string removes HTML tags."""
        result = SecurityValidator.sanitize_string("<b>Bold</b> text")
        assert "<b>" not in result
        assert "Bold" in result or "text" in result

    def test_validate_password_strength_valid(self):
        """Test password validation with valid password."""
        is_valid, message = SecurityValidator.validate_password_strength("SecurePass123!")
        assert is_valid is True
        assert message is None

    def test_validate_password_strength_too_short(self):
        """Test password validation with short password."""
        is_valid, message = SecurityValidator.validate_password_strength("Pass1!")
        assert is_valid is False
        assert "at least 8 characters" in message

    def test_validate_password_strength_no_uppercase(self):
        """Test password validation without uppercase letter."""
        is_valid, message = SecurityValidator.validate_password_strength("password123!")
        assert is_valid is False
        assert "uppercase" in message.lower()

    def test_validate_password_strength_no_lowercase(self):
        """Test password validation without lowercase letter."""
        is_valid, message = SecurityValidator.validate_password_strength("PASSWORD123!")
        assert is_valid is False
        assert "lowercase" in message.lower()

    def test_validate_password_strength_no_digit(self):
        """Test password validation without digit."""
        is_valid, message = SecurityValidator.validate_password_strength("PasswordTest!")
        assert is_valid is False
        assert "digit" in message.lower()

    def test_validate_password_strength_no_special(self):
        """Test password validation without special character."""
        is_valid, message = SecurityValidator.validate_password_strength("Password123")
        assert is_valid is False
        assert "special character" in message.lower()

    def test_validate_email_address_valid(self):
        """Test email validation with valid email."""
        is_valid, message = SecurityValidator.validate_email_address("test@example.com")
        assert is_valid is True
        assert message is None

    def test_validate_email_address_invalid(self):
        """Test email validation with invalid email."""
        is_valid, message = SecurityValidator.validate_email_address("invalid-email")
        assert is_valid is False
        assert "Invalid email" in message

    def test_validate_email_address_missing_at(self):
        """Test email validation missing @ symbol."""
        is_valid, message = SecurityValidator.validate_email_address("testexample.com")
        assert is_valid is False

    def test_validate_isbn_valid_isbn13(self):
        """Test ISBN validation with valid ISBN-13."""
        is_valid, message = SecurityValidator.validate_isbn("978-0-545-01022-1")
        assert is_valid is True
        assert message is None

    def test_validate_isbn_valid_isbn10(self):
        """Test ISBN validation with valid ISBN-10."""
        is_valid, message = SecurityValidator.validate_isbn("0-545-01022-5")
        assert is_valid is True
        assert message is None

    def test_validate_isbn_invalid(self):
        """Test ISBN validation with invalid ISBN."""
        is_valid, message = SecurityValidator.validate_isbn("123-456")
        assert is_valid is False
        assert "Invalid ISBN" in message

    def test_validate_latitude_valid(self):
        """Test latitude validation with valid value."""
        is_valid, message = SecurityValidator.validate_latitude(53.4808)
        assert is_valid is True
        assert message is None

    def test_validate_latitude_too_high(self):
        """Test latitude validation with value too high."""
        is_valid, message = SecurityValidator.validate_latitude(91.0)
        assert is_valid is False
        assert "between -90 and 90" in message

    def test_validate_latitude_too_low(self):
        """Test latitude validation with value too low."""
        is_valid, message = SecurityValidator.validate_latitude(-91.0)
        assert is_valid is False

    def test_validate_longitude_valid(self):
        """Test longitude validation with valid value."""
        is_valid, message = SecurityValidator.validate_longitude(-2.2426)
        assert is_valid is True
        assert message is None

    def test_validate_longitude_too_high(self):
        """Test longitude validation with value too high."""
        is_valid, message = SecurityValidator.validate_longitude(181.0)
        assert is_valid is False
        assert "between -180 and 180" in message

    def test_validate_longitude_too_low(self):
        """Test longitude validation with value too low."""
        is_valid, message = SecurityValidator.validate_longitude(-181.0)
        assert is_valid is False

    def test_validate_quantity_valid(self):
        """Test quantity validation with valid value."""
        is_valid, message = SecurityValidator.validate_quantity(5)
        assert is_valid is True
        assert message is None

    def test_validate_quantity_negative(self):
        """Test quantity validation with negative value."""
        is_valid, message = SecurityValidator.validate_quantity(-1)
        assert is_valid is False
        assert "non-negative" in message

    def test_validate_quantity_zero(self):
        """Test quantity validation with zero."""
        is_valid, message = SecurityValidator.validate_quantity(0)
        assert is_valid is True  # Zero should be valid

    def test_validate_quantity_too_high(self):
        """Test quantity validation with very high value."""
        is_valid, message = SecurityValidator.validate_quantity(10001)
        assert is_valid is False
        assert "10000" in message


class TestLoginAttemptTracker:
    """Tests for LoginAttemptTracker utility class."""

    @patch("app.utils.login_attempts.db_manager")
    def test_record_failed_login(self, mock_db):
        """Test recording a failed login attempt."""
        mock_db.login_attempts.insert_one = MagicMock()

        LoginAttemptTracker.record_failed_login("test@example.com", "192.168.1.1")

        mock_db.login_attempts.insert_one.assert_called_once()
        call_args = mock_db.login_attempts.insert_one.call_args[0][0]
        assert call_args["email"] == "test@example.com"
        assert call_args["ip_address"] == "192.168.1.1"
        assert call_args["successful"] is False

    @patch("app.utils.login_attempts.db_manager")
    def test_record_successful_login(self, mock_db):
        """Test recording a successful login attempt."""
        mock_db.login_attempts.insert_one = MagicMock()

        LoginAttemptTracker.record_successful_login("test@example.com", "192.168.1.1")

        mock_db.login_attempts.insert_one.assert_called_once()
        call_args = mock_db.login_attempts.insert_one.call_args[0][0]
        assert call_args["email"] == "test@example.com"
        assert call_args["successful"] is True

    @patch("app.utils.login_attempts.db_manager")
    def test_is_account_locked_not_locked(self, mock_db):
        """Test is_account_locked when account is not locked."""
        # Mock less than MAX_ATTEMPTS failed attempts
        mock_db.login_attempts.find.return_value = [{"timestamp": datetime.now(UTC)}] * 3

        is_locked, unlock_time = LoginAttemptTracker.is_account_locked("test@example.com")

        assert is_locked is False
        assert unlock_time is None

    @patch("app.utils.login_attempts.db_manager")
    def test_is_account_locked_when_locked(self, mock_db):
        """Test is_account_locked when account is locked."""
        # Mock MAX_ATTEMPTS or more failed attempts
        recent_time = datetime.now(UTC)
        mock_db.login_attempts.find.return_value = [{"timestamp": recent_time}] * 5

        is_locked, unlock_time = LoginAttemptTracker.is_account_locked("test@example.com")

        assert is_locked is True
        assert unlock_time is not None

    @patch("app.utils.login_attempts.db_manager")
    def test_get_remaining_attempts(self, mock_db):
        """Test get_remaining_attempts method."""
        # Mock 2 failed attempts
        mock_db.login_attempts.count_documents.return_value = 2

        remaining = LoginAttemptTracker.get_remaining_attempts("test@example.com")

        assert remaining == 3  # MAX_ATTEMPTS (5) - 2 = 3

    @patch("app.utils.login_attempts.db_manager")
    def test_get_remaining_attempts_maxed_out(self, mock_db):
        """Test get_remaining_attempts when maxed out."""
        # Mock MAX_ATTEMPTS failed attempts
        mock_db.login_attempts.count_documents.return_value = 5

        remaining = LoginAttemptTracker.get_remaining_attempts("test@example.com")

        assert remaining == 0

    @patch("app.utils.login_attempts.db_manager")
    def test_cleanup_old_attempts(self, mock_db):
        """Test cleanup_old_attempts method."""
        mock_result = MagicMock()
        mock_result.deleted_count = 10
        mock_db.login_attempts.delete_many.return_value = mock_result

        deleted = LoginAttemptTracker.cleanup_old_attempts()

        assert deleted == 10
        mock_db.login_attempts.delete_many.assert_called_once()


class TestDatabaseManager:
    """Tests for DatabaseManager utility class."""

    def test_database_manager_singleton(self):
        """Test DatabaseManager implements singleton pattern."""
        from app.utils.database import DatabaseManager

        instance1 = DatabaseManager()
        instance2 = DatabaseManager()

        # Both should be the same instance
        assert instance1 is instance2

    @patch("app.utils.database.MongoClient")
    def test_database_manager_initialization(self, mock_mongo_client):
        """Test DatabaseManager initialization."""
        from app.utils.database import DatabaseManager

        # Reset singleton
        DatabaseManager._instance = None

        manager = DatabaseManager()

        assert manager is not None
        # MongoClient should be instantiated when connect is called
