"""Book and inventory management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime

from app.models import Book, Inventory, SearchIndex
from app.utils.database import db_manager

book_bp = Blueprint("book_routes", __name__)


@book_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_book():
    """Add a new book to inventory.

    Returns:
        Rendered add book template or redirect to dashboard
    """
    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
        cover_url = request.form.get("cover_url")
        qty = request.form.get("qty", type=int)
        condition = request.form.get("condition", "new")

        # Validate required fields
        if not all([isbn, title, author, qty is not None]):
            flash("All required fields must be filled", "error")
            return render_template("books/add.html")

        # Check if book exists, if not create it
        existing_book = db_manager.books.find_one({"isbn": isbn})

        if not existing_book:
            # Create new book
            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                cover_url=cover_url if cover_url else None,
            )
            db_manager.books.insert_one(book.to_dict())

            # Create search index
            search_index = SearchIndex.create_from_book(isbn, title, author)
            db_manager.search_index.insert_one(search_index.to_dict())

        # Check if inventory already exists for this store and book
        existing_inventory = db_manager.inventory.find_one({
            "store_id": current_user._id,
            "isbn": isbn
        })

        if existing_inventory:
            # Update existing inventory
            db_manager.inventory.update_one(
                {"_id": existing_inventory["_id"]},
                {
                    "$set": {
                        "qty": qty,
                        "condition": condition,
                        "last_updated": datetime.utcnow()
                    }
                }
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

    return render_template("books/add.html")


@book_bp.route("/edit/<isbn>", methods=["GET", "POST"])
@login_required
def edit_book(isbn):
    """Edit book inventory.

    Args:
        isbn: Book ISBN

    Returns:
        Rendered edit book template or redirect to dashboard
    """
    # Get inventory for current store and book
    inventory_data = db_manager.inventory.find_one({
        "store_id": current_user._id,
        "isbn": isbn
    })

    if not inventory_data:
        flash("Book not found in your inventory", "error")
        return redirect(url_for("store_routes.dashboard"))

    book_data = db_manager.books.find_one({"isbn": isbn})

    if request.method == "POST":
        qty = request.form.get("qty", type=int)
        condition = request.form.get("condition")

        # Update inventory
        db_manager.inventory.update_one(
            {"_id": inventory_data["_id"]},
            {
                "$set": {
                    "qty": qty,
                    "condition": condition,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        flash("Book inventory updated successfully", "success")
        return redirect(url_for("store_routes.dashboard"))

    return render_template("books/edit.html", inventory=inventory_data, book=book_data)


@book_bp.route("/delete/<isbn>", methods=["POST"])
@login_required
def delete_book(isbn):
    """Delete book from inventory.

    Args:
        isbn: Book ISBN

    Returns:
        Redirect to dashboard
    """
    # Delete inventory entry
    result = db_manager.inventory.delete_one({
        "store_id": current_user._id,
        "isbn": isbn
    })

    if result.deleted_count > 0:
        flash("Book removed from inventory", "success")
    else:
        flash("Book not found in your inventory", "error")

    return redirect(url_for("store_routes.dashboard"))


@book_bp.route("/<isbn>")
def book_detail(isbn):
    """View book details and availability.

    Args:
        isbn: Book ISBN

    Returns:
        Rendered book detail template
    """
    # Get book data
    book_data = db_manager.books.find_one({"isbn": isbn})

    if not book_data:
        flash("Book not found", "error")
        return redirect(url_for("main.index"))

    # Get all inventory entries for this book
    inventory_data = list(db_manager.inventory.find({"isbn": isbn, "qty": {"$gt": 0}}))

    # Get store details for each inventory entry
    inventory_with_stores = []
    for inv in inventory_data:
        store_data = db_manager.stores.find_one({"_id": inv["store_id"]})
        if store_data:
            inventory_with_stores.append({
                "inventory": inv,
                "store": store_data
            })

    return render_template(
        "books/detail.html",
        book=book_data,
        inventory=inventory_with_stores
    )
