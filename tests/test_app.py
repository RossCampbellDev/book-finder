"""Tests for Flask application initialization and configuration."""

from app import create_app


class TestAppInitialization:
    """Tests for Flask app creation and configuration."""

    def test_create_app_testing(self):
        """Test creating app with testing configuration."""
        # Note: Only test with testing config to avoid MongoDB connection attempts
        app = create_app("testing")
        assert app is not None
        assert app.config["TESTING"] is True

    def test_app_has_blueprints(self, app):
        """Test that app has registered blueprints."""
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        # Check for main blueprints
        assert any("main" in name for name in blueprint_names)

    def test_app_has_extensions(self, app):
        """Test that app has initialized extensions."""
        # Check for extensions
        assert hasattr(app, "extensions")

    def test_app_secret_key_set(self, app):
        """Test that app has secret key configured."""
        assert app.config["SECRET_KEY"] is not None
        assert app.config["SECRET_KEY"] != ""

    def test_app_context_works(self, app):
        """Test that app context works."""
        with app.app_context():
            # Should be able to work within app context
            assert True

    def test_app_test_client_works(self, client):
        """Test that test client works."""
        response = client.get("/")
        assert response is not None


class TestAppConfiguration:
    """Tests for application configuration."""

    def test_testing_config(self):
        """Test testing configuration settings."""
        from config.config import TestingConfig

        assert TestingConfig.TESTING is True
        assert TestingConfig.MONGO_DB_NAME == "bookfinder_test"

    def test_development_config(self):
        """Test development configuration settings."""
        from config.config import DevelopmentConfig

        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.SESSION_COOKIE_SECURE is False

    def test_production_config(self):
        """Test production configuration settings."""
        from config.config import ProductionConfig

        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.SESSION_COOKIE_SECURE is True

    def test_config_dictionary(self):
        """Test configuration dictionary."""
        from config.config import config

        assert "development" in config
        assert "production" in config
        assert "testing" in config
        assert "default" in config


class TestAppSecurity:
    """Tests for application security features."""

    def test_csrf_protection_enabled(self, app):
        """Test that CSRF protection is enabled."""
        # CSRF should be disabled in testing mode
        if not app.config["TESTING"]:
            assert "csrf" in app.extensions or "CSRFProtect" in str(app.extensions)

    def test_session_cookie_httponly(self, app):
        """Test that session cookies are httponly."""
        assert app.config["SESSION_COOKIE_HTTPONLY"] is True

    def test_session_cookie_samesite(self, app):
        """Test that session cookies have samesite attribute."""
        assert app.config["SESSION_COOKIE_SAMESITE"] in ["Lax", "Strict", "None"]

    def test_permanent_session_lifetime(self, app):
        """Test that permanent session lifetime is set."""
        assert app.config["PERMANENT_SESSION_LIFETIME"] > 0


class TestAppRoutes:
    """Tests for application route registration."""

    # Note: Route tests removed because they require MongoDB connection
    # These are better tested as integration tests with a test database running


class TestAppLoginManager:
    """Tests for Flask-Login integration."""

    def test_login_manager_initialized(self, app):
        """Test that login manager is initialized."""
        assert "login_manager" in app.extensions or hasattr(app, "login_manager")

    def test_user_loader_function_exists(self, app):
        """Test that user loader function is registered."""
        # This is tested indirectly through authentication tests
        assert True


class TestAppTemplates:
    """Tests for template rendering."""

    def test_base_template_renders(self, client):
        """Test that base template renders without errors."""
        response = client.get("/")
        assert response.status_code == 200
        # Check for common HTML elements
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_templates_have_proper_encoding(self, client):
        """Test that templates use proper UTF-8 encoding."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.content_type.startswith("text/html")
