"""Route blueprints for the book finder application."""
from app.routes.main_routes import main_bp
from app.routes.store_routes import store_bp
from app.routes.book_routes import book_bp
from app.routes.search_routes import search_bp

__all__ = ["main_bp", "store_bp", "book_bp", "search_bp"]