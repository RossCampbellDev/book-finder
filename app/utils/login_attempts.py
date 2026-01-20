"""Login attempt tracking and account lockout functionality."""

from datetime import UTC, datetime, timedelta

from app.utils.database import db_manager


class LoginAttemptTracker:
    """Tracks failed login attempts and implements account lockout."""

    MAX_ATTEMPTS = 5  # Maximum failed login attempts
    LOCKOUT_DURATION = timedelta(minutes=15)  # Lockout duration
    ATTEMPT_WINDOW = timedelta(minutes=30)  # Time window to count attempts

    @staticmethod
    def record_failed_attempt(email: str, ip_address: str) -> None:
        """Record a failed login attempt.

        Args:
            email: Email address that failed to login
            ip_address: IP address of the request
        """
        db_manager.login_attempts.insert_one(
            {
                "email": email.lower(),
                "ip_address": ip_address,
                "timestamp": datetime.now(UTC),
                "successful": False,
            }
        )

    @staticmethod
    def record_successful_login(email: str, ip_address: str) -> None:
        """Record a successful login and clear failed attempts.

        Args:
            email: Email address that logged in successfully
            ip_address: IP address of the request
        """
        # Record successful login
        db_manager.login_attempts.insert_one(
            {
                "email": email.lower(),
                "ip_address": ip_address,
                "timestamp": datetime.now(UTC),
                "successful": True,
            }
        )

        # Clear old failed attempts for this email
        db_manager.login_attempts.delete_many({"email": email.lower(), "successful": False})

    @staticmethod
    def is_account_locked(email: str) -> tuple[bool, datetime | None]:
        """Check if an account is locked due to too many failed attempts.

        Args:
            email: Email address to check

        Returns:
            Tuple of (is_locked, unlock_time)
        """
        # Get recent failed attempts
        cutoff_time = datetime.now(UTC) - LoginAttemptTracker.ATTEMPT_WINDOW

        failed_attempts = list(
            db_manager.login_attempts.find(
                {"email": email.lower(), "successful": False, "timestamp": {"$gte": cutoff_time}}
            ).sort("timestamp", -1)
        )

        if len(failed_attempts) >= LoginAttemptTracker.MAX_ATTEMPTS:
            # Account is locked - calculate unlock time
            latest_attempt = failed_attempts[0]["timestamp"]
            unlock_time = latest_attempt + LoginAttemptTracker.LOCKOUT_DURATION

            # Check if still locked
            if datetime.now(UTC) < unlock_time:
                return True, unlock_time
            # Lockout period has expired, clear old attempts
            db_manager.login_attempts.delete_many(
                {"email": email.lower(), "successful": False, "timestamp": {"$lt": unlock_time}}
            )
            return False, None

        return False, None

    @staticmethod
    def get_remaining_attempts(email: str) -> int:
        """Get the number of remaining login attempts before lockout.

        Args:
            email: Email address to check

        Returns:
            Number of remaining attempts
        """
        cutoff_time = datetime.now(UTC) - LoginAttemptTracker.ATTEMPT_WINDOW

        failed_count = db_manager.login_attempts.count_documents(
            {"email": email.lower(), "successful": False, "timestamp": {"$gte": cutoff_time}}
        )

        remaining = LoginAttemptTracker.MAX_ATTEMPTS - failed_count
        return max(0, remaining)

    @staticmethod
    def cleanup_old_attempts() -> int:
        """Clean up old login attempt records.

        Returns:
            Number of records deleted
        """
        cutoff_time = datetime.now(UTC) - timedelta(days=30)

        result = db_manager.login_attempts.delete_many({"timestamp": {"$lt": cutoff_time}})

        return result.deleted_count
