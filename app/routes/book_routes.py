"""Book and inventory management routes."""

from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user, login_required

from app.models import Book, Inventory, SearchIndex
from app.utils.database import db_manager
from app.utils.security import SecurityValidator

book_bp = Blueprint("book_routes", __name__)

# Initialize rate limiter for this blueprint
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


@book_bp.route("/add", methods=["GET", "POST"])
@login_required
@limiter.limit("20 per hour")
def add_book():
    """Add a new book to inventory with input validation.

    Returns:
        Rendered add book template or redirect to dashboard
    """
    if request.method == "POST":
        try:
            # Get and sanitize form data
            isbn = request.form.get("isbn", "").strip()
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            cover_url = request.form.get("cover_url", "").strip()
            qty = request.form.get("qty", type=int)
            condition = request.form.get("condition", "new")

            # Validate required fields
            if not all([isbn, title, author, qty is not None]):
                flash("All required fields must be filled", "error")
                return render_template("books/add.html")

            # Validate ISBN
            is_valid_isbn, isbn_error = SecurityValidator.validate_isbn(isbn)
            if not is_valid_isbn:
                flash(isbn_error, "error")
                return render_template("books/add.html")

            # Sanitize string fields
            safe_title = SecurityValidator.sanitize_string(title, max_length=500)
            safe_author = SecurityValidator.sanitize_string(author, max_length=200)

            # Validate quantity
            is_valid_qty, qty_error = SecurityValidator.validate_quantity(qty)
            if not is_valid_qty:
                flash(qty_error, "error")
                return render_template("books/add.html")

            # Validate condition (whitelist approach)
            allowed_conditions = ["new", "like_new", "good", "acceptable", "poor"]
            if condition not in allowed_conditions:
                condition = "good"

            # Sanitize cover_url if provided
            safe_cover_url = None
            if cover_url:
                safe_cover_url = SecurityValidator.sanitize_string(cover_url, max_length=500)
                if not safe_cover_url.startswith(("http://", "https://")):
                    flash("Cover URL must start with http:// or https://", "error")
                    return render_template("books/add.html")

            # Check if book exists, if not create it
            existing_book = db_manager.books.find_one({"isbn": isbn})

            if not existing_book:
                # Create new book
                book = Book(
                    isbn=isbn,
                    title=safe_title,
                    author=safe_author,
                    cover_url=safe_cover_url,
                )
                db_manager.books.insert_one(book.to_dict())

                # Create search index
                search_index = SearchIndex.create_from_book(isbn, safe_title, safe_author)
                db_manager.search_index.insert_one(search_index.to_dict())

            # Check if inventory already exists for this store and book
            existing_inventory = db_manager.inventory.find_one(
                {"store_id": current_user._id, "isbn": isbn}
            )

            if existing_inventory:
                # Update existing inventory
                db_manager.inventory.update_one(
                    {"_id": existing_inventory["_id"]},
                    {
                        "$set": {
                            "qty": qty,
                            "condition": condition,
                            "last_updated": datetime.now(UTC),
                        }
                    },
                )
                flash("Book inventory updated successfully", "success")
            else:
                # Create new inventory entry
                inventory = Inventory(
                    store_id=current_user._id,
                    isbn=isbn,
                    qty=qty,
                    condition=condition,
                )
                db_manager.inventory.insert_one(inventory.to_dict())
                flash("Book added to inventory successfully", "success")

            return redirect(url_for("store_routes.dashboard"))

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "error")
            return render_template("books/add.html")
        except Exception:
            flash("An error occurred while adding the book. Please try again.", "error")
            return render_template("books/add.html")

    return render_template("books/add.html")


@book_bp.route("/edit/<isbn>", methods=["GET", "POST"])
@login_required
def edit_book(isbn):
    """Edit book inventory with input validation.

    Args:
        isbn: Book ISBN

    Returns:
        Rendered edit book template or redirect to dashboard
    """
    try:
        # Sanitize ISBN parameter
        safe_isbn = SecurityValidator.sanitize_string(isbn, max_length=20)

        # Get inventory for current store and book
        inventory_data = db_manager.inventory.find_one(
            {"store_id": current_user._id, "isbn": safe_isbn}
        )

        if not inventory_data:
            flash("Book not found in your inventory", "error")
            return redirect(url_for("store_routes.dashboard"))

        book_data = db_manager.books.find_one({"isbn": safe_isbn})

        if request.method == "POST":
            qty = request.form.get("qty", type=int)
            condition = request.form.get("condition", "good")

            # Validate quantity
            is_valid_qty, qty_error = SecurityValidator.validate_quantity(qty)
            if not is_valid_qty:
                flash(qty_error, "error")
                return render_template("books/edit.html", inventory=inventory_data, book=book_data)

            # Validate condition (whitelist approach)
            allowed_conditions = ["new", "like_new", "good", "acceptable", "poor"]
            if condition not in allowed_conditions:
                flash("Invalid condition value", "error")
                return render_template("books/edit.html", inventory=inventory_data, book=book_data)

            # Update inventory
            db_manager.inventory.update_one(
                {"_id": inventory_data["_id"]},
                {"$set": {"qty": qty, "condition": condition, "last_updated": datetime.now(UTC)}},
            )
            flash("Book inventory updated successfully", "success")
            return redirect(url_for("store_routes.dashboard"))

        return render_template("books/edit.html", inventory=inventory_data, book=book_data)

    except ValueError as e:
        flash(f"Invalid input: {str(e)}", "error")
        return redirect(url_for("store_routes.dashboard"))
    except Exception:
        flash("An error occurred while editing the book. Please try again.", "error")
        return redirect(url_for("store_routes.dashboard"))


@book_bp.route("/delete/<isbn>", methods=["POST"])
@login_required
def delete_book(isbn):
    """Delete book from inventory with input validation.

    Args:
        isbn: Book ISBN

    Returns:
        Redirect to dashboard
    """
    try:
        # Sanitize ISBN parameter
        safe_isbn = SecurityValidator.sanitize_string(isbn, max_length=20)

        # Delete inventory entry
        result = db_manager.inventory.delete_one({"store_id": current_user._id, "isbn": safe_isbn})

        if result.deleted_count > 0:
            flash("Book removed from inventory", "success")
        else:
            flash("Book not found in your inventory", "error")

        return redirect(url_for("store_routes.dashboard"))

    except ValueError as e:
        flash(f"Invalid input: {str(e)}", "error")
        return redirect(url_for("store_routes.dashboard"))
    except Exception:
        flash("An error occurred while deleting the book. Please try again.", "error")
        return redirect(url_for("store_routes.dashboard"))


@book_bp.route("/<isbn>")
def book_detail(isbn):
    """View book details and availability with input validation.

    Args:
        isbn: Book ISBN

    Returns:
        Rendered book detail template
    """
    try:
        # Sanitize ISBN parameter
        safe_isbn = SecurityValidator.sanitize_string(isbn, max_length=20)

        # Get book data
        book_data = db_manager.books.find_one({"isbn": safe_isbn})

        if not book_data:
            flash("Book not found", "error")
            return redirect(url_for("main.index"))

        # Get all inventory entries for this book
        inventory_data = list(db_manager.inventory.find({"isbn": safe_isbn, "qty": {"$gt": 0}}))

        # Get store details for each inventory entry
        inventory_with_stores = []
        for inv in inventory_data:
            store_data = db_manager.stores.find_one({"_id": inv["store_id"]})
            if store_data:
                inventory_with_stores.append({"inventory": inv, "store": store_data})

        return render_template("books/detail.html", book=book_data, inventory=inventory_with_stores)

    except ValueError as e:
        flash(f"Invalid input: {str(e)}", "error")
        return redirect(url_for("main.index"))
    except Exception:
        flash("An error occurred while loading book details. Please try again.", "error")
        return redirect(url_for("main.index"))
