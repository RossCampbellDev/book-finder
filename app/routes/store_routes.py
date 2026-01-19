"""Store management and authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
from bson import ObjectId

from app.models import Store
from app.utils.database import db_manager

store_bp = Blueprint("store_routes", __name__)


@store_bp.route("/login", methods=["GET", "POST"])
def login():
    """Store login page.

    Returns:
        Rendered login template or redirect to dashboard
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("store/login.html")

        # Find store by email
        store_data = db_manager.stores.find_one({"email": email})

        if store_data and store_data.get("password_hash"):
            # Verify password
            if bcrypt.checkpw(password.encode("utf-8"), store_data["password_hash"]):
                store = Store.from_dict(store_data)
                login_user(store)
                flash(f"Welcome back, {store.name}!", "success")
                return redirect(url_for("store_routes.dashboard"))

        flash("Invalid email or password", "error")

    return render_template("store/login.html")


@store_bp.route("/register", methods=["GET", "POST"])
def register():
    """Store registration page.

    Returns:
        Rendered registration template or redirect to dashboard
    """
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        store_type = request.form.get("store_type", "bookstore")
        address = request.form.get("address")
        latitude = request.form.get("latitude", type=float)
        longitude = request.form.get("longitude", type=float)
        hours = request.form.get("hours")
        contact = request.form.get("contact")
        website = request.form.get("website")

        # Validate required fields
        if not all([name, email, password, address, latitude, longitude, hours, contact]):
            flash("All required fields must be filled", "error")
            return render_template("store/register.html")

        # Check if email already exists
        existing_store = db_manager.stores.find_one({"email": email})
        if existing_store:
            flash("Email already registered", "error")
            return render_template("store/register.html")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Create store
        store = Store(
            name=name,
            email=email,
            password_hash=password_hash,
            store_type=store_type,
            address=address,
            latitude=latitude,
            longitude=longitude,
            hours=hours,
            contact=contact,
            website=website if website else None,
        )

        # Insert into database
        result = db_manager.stores.insert_one(store.to_dict())
        store._id = result.inserted_id

        # Log in the user
        login_user(store)
        flash("Registration successful! Welcome!", "success")
        return redirect(url_for("store_routes.dashboard"))

    return render_template("store/register.html")


@store_bp.route("/logout")
@login_required
def logout():
    """Log out the current store user.

    Returns:
        Redirect to home page
    """
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("main.index"))


@store_bp.route("/dashboard")
@login_required
def dashboard():
    """Store dashboard page.

    Returns:
        Rendered dashboard template
    """
    # Get store inventory
    inventory_data = list(db_manager.inventory.find({"store_id": current_user._id}))

    # Get book details for inventory items
    inventory_with_books = []
    for inv in inventory_data:
        book_data = db_manager.books.find_one({"isbn": inv["isbn"]})
        inventory_with_books.append({
            "inventory": inv,
            "book": book_data
        })

    return render_template("store/dashboard.html", inventory=inventory_with_books)


@store_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Store profile management page.

    Returns:
        Rendered profile template or redirect to dashboard
    """
    if request.method == "POST":
        # Update store information
        update_data = {}

        fields = ["name", "address", "hours", "contact", "website"]
        for field in fields:
            value = request.form.get(field)
            if value:
                if field == "name":
                    update_data["name"] = value
                elif field == "address":
                    update_data["address"] = value
                elif field == "hours":
                    update_data["hours"] = value
                elif field == "contact":
                    update_data["contact"] = value
                elif field == "website":
                    update_data["website"] = value

        # Update location if provided
        latitude = request.form.get("latitude", type=float)
        longitude = request.form.get("longitude", type=float)
        if latitude is not None and longitude is not None:
            update_data["location"] = {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }

        if update_data:
            db_manager.stores.update_one(
                {"_id": current_user._id},
                {"$set": update_data}
            )
            flash("Profile updated successfully", "success")

        return redirect(url_for("store_routes.dashboard"))

    return render_template("store/profile.html")
