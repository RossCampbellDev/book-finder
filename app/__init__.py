"""Flask application factory."""
import os
from flask import Flask
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from config.config import config
from app.utils.database import db_manager


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configured Flask application instance
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Configure session security
    app.config['SESSION_COOKIE_SECURE'] = config_name == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

    # Generate secret key if not set
    if not app.config.get('SECRET_KEY'):
        import secrets
        app.config['SECRET_KEY'] = secrets.token_hex(32)

    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window"
    )

    # Initialize security headers (Talisman)
    # Only enforce HTTPS in production
    if config_name == 'production':
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            content_security_policy={
                'default-src': "'self'",
                'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
                'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
                'img-src': ["'self'", "data:", "https:"],
            }
        )
    else:
        # Development mode - less strict
        Talisman(
            app,
            force_https=False,
            content_security_policy=None
        )

    # Initialize database
    db_manager.connect(
        uri=app.config["MONGO_URI"],
        db_name=app.config["MONGO_DB_NAME"]
    )

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "store_routes.login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login.

        Args:
            user_id: User ID (store ObjectId as string)

        Returns:
            Store instance or None
        """
        from bson import ObjectId
        from app.models import Store

        try:
            store_data = db_manager.stores.find_one({"_id": ObjectId(user_id)})
            if store_data:
                return Store.from_dict(store_data)
        except Exception:
            pass
        return None

    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.store_routes import store_bp
    from app.routes.book_routes import book_bp
    from app.routes.search_routes import search_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(store_bp, url_prefix="/store")
    app.register_blueprint(book_bp, url_prefix="/books")
    app.register_blueprint(search_bp, url_prefix="/search")

    return app