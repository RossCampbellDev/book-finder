"""Main routes for the book finder application."""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home page with search interface.

    Returns:
        Rendered home page template
    """
    return render_template("index.html")


@main_bp.route("/about")
def about():
    """About page.

    Returns:
        Rendered about page template
    """
    return render_template("about.html")
