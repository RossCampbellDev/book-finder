"""Store management and authentication routes."""

from datetime import UTC, datetime

import bcrypt
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user, login_required, login_user, logout_user

from app.models import Store
from app.utils.database import db_manager
from app.utils.login_attempts import LoginAttemptTracker
from app.utils.security import SecurityValidator

store_bp = Blueprint("store_routes", __name__)

# Initialize rate limiter for this blueprint
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


@store_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    """Store login page with rate limiting and account lockout.

    Returns:
        Rendered login template or redirect to dashboard
    """
    if request.method == "POST":
        try:
            # Get and sanitize input
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required", "error")
                return render_template("store/login.html")

            # Validate email format
            is_valid_email, email_error = SecurityValidator.validate_email_address(email)
            if not is_valid_email:
                flash("Invalid email format", "error")
                return render_template("store/login.html")

            # Use normalized email
            email = email_error  # email_error contains normalized email on success

            # Check if account is locked
            is_locked, unlock_time = LoginAttemptTracker.is_account_locked(email)
            if is_locked:
                remaining = (unlock_time - datetime.now(UTC)).seconds // 60
                flash(
                    f"Account is locked due to too many failed attempts. Try again in {remaining} minutes.",
                    "error",
                )
                return render_template("store/login.html")

            # Sanitize email to prevent NoSQL injection
            safe_email = SecurityValidator.sanitize_input(email)

            # Find store by email
            store_data = db_manager.stores.find_one({"email": safe_email})

            if (
                store_data
                and store_data.get("password_hash")
                and bcrypt.checkpw(password.encode("utf-8"), store_data["password_hash"])
            ):
                store = Store.from_dict(store_data)
                login_user(store)

                # Record successful login
                LoginAttemptTracker.record_successful_login(email, request.remote_addr)

                flash(f"Welcome back, {store.name}!", "success")
                return redirect(url_for("store_routes.dashboard"))

            # Record failed attempt
            LoginAttemptTracker.record_failed_attempt(email, request.remote_addr)

            # Get remaining attempts
            remaining_attempts = LoginAttemptTracker.get_remaining_attempts(email)
            if remaining_attempts > 0:
                flash(
                    f"Invalid email or password. {remaining_attempts} attempts remaining.", "error"
                )
            else:
                flash("Too many failed attempts. Account locked for 15 minutes.", "error")

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "error")
        except Exception:
            flash("An error occurred during login. Please try again.", "error")

    return render_template("store/login.html")


@store_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def register():
    """Store registration page with input validation and rate limiting.

    Returns:
        Rendered registration template or redirect to dashboard
    """
    if request.method == "POST":
        try:
            # Get and sanitize form data
            name = SecurityValidator.sanitize_string(request.form.get("name", ""), max_length=200)
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            store_type = request.form.get("store_type", "bookstore")
            address = SecurityValidator.sanitize_string(
                request.form.get("address", ""), max_length=500
            )
            latitude = request.form.get("latitude", type=float)
            longitude = request.form.get("longitude", type=float)
            hours = SecurityValidator.sanitize_string(request.form.get("hours", ""), max_length=200)
            contact = SecurityValidator.sanitize_string(
                request.form.get("contact", ""), max_length=50
            )
            website = request.form.get("website", "").strip()

            # Validate required fields
            if not all(
                [
                    name,
                    email,
                    password,
                    address,
                    latitude is not None,
                    longitude is not None,
                    hours,
                    contact,
                ]
            ):
                flash("All required fields must be filled", "error")
                return render_template("store/register.html")

            # Validate email
            is_valid_email, email_result = SecurityValidator.validate_email_address(email)
            if not is_valid_email:
                flash(f"Invalid email: {email_result}", "error")
                return render_template("store/register.html")
            email = email_result  # Use normalized email

            # Validate password strength
            is_valid_password, password_error = SecurityValidator.validate_password_strength(
                password
            )
            if not is_valid_password:
                flash(password_error, "error")
                return render_template("store/register.html")

            # Validate coordinates
            is_valid_lat, lat_error = SecurityValidator.validate_latitude(latitude)
            if not is_valid_lat:
                flash(lat_error, "error")
                return render_template("store/register.html")

            is_valid_lng, lng_error = SecurityValidator.validate_longitude(longitude)
            if not is_valid_lng:
                flash(lng_error, "error")
                return render_template("store/register.html")

            # Validate store_type (whitelist approach)
            allowed_types = ["bookstore", "library", "thrift"]
            if store_type not in allowed_types:
                store_type = "bookstore"

            # Sanitize website URL
            if website:
                website = SecurityValidator.sanitize_string(website, max_length=500)
                if not website.startswith(("http://", "https://")):
                    flash("Website must start with http:// or https://", "error")
                    return render_template("store/register.html")

            # Check if email already exists (with sanitized email)
            safe_email = SecurityValidator.sanitize_input(email)
            existing_store = db_manager.stores.find_one({"email": safe_email})
            if existing_store:
                flash("Email already registered", "error")
                return render_template("store/register.html")

            # Hash password
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            # Create store
            store = Store(
                name=name,
                email=safe_email,
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

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "error")
            return render_template("store/register.html")
        except Exception:
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("store/register.html")

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
        inventory_with_books.append({"inventory": inv, "book": book_data})

    return render_template("store/dashboard.html", inventory=inventory_with_books)


@store_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Store profile management page with input validation.

    Returns:
        Rendered profile template or redirect to dashboard
    """
    if request.method == "POST":
        try:
            # Update store information
            update_data = {}

            # Sanitize and validate string fields
            name = request.form.get("name")
            if name:
                update_data["name"] = SecurityValidator.sanitize_string(name, max_length=200)

            address = request.form.get("address")
            if address:
                update_data["address"] = SecurityValidator.sanitize_string(address, max_length=500)

            hours = request.form.get("hours")
            if hours:
                update_data["hours"] = SecurityValidator.sanitize_string(hours, max_length=200)

            contact = request.form.get("contact")
            if contact:
                update_data["contact"] = SecurityValidator.sanitize_string(contact, max_length=50)

            website = request.form.get("website")
            if website:
                website = SecurityValidator.sanitize_string(website, max_length=500)
                if not website.startswith(("http://", "https://")):
                    flash("Website must start with http:// or https://", "error")
                    return render_template("store/profile.html")
                update_data["website"] = website

            # Update location if provided
            latitude = request.form.get("latitude", type=float)
            longitude = request.form.get("longitude", type=float)
            if latitude is not None and longitude is not None:
                # Validate coordinates
                is_valid_lat, lat_error = SecurityValidator.validate_latitude(latitude)
                if not is_valid_lat:
                    flash(lat_error, "error")
                    return render_template("store/profile.html")

                is_valid_lng, lng_error = SecurityValidator.validate_longitude(longitude)
                if not is_valid_lng:
                    flash(lng_error, "error")
                    return render_template("store/profile.html")

                update_data["location"] = {"type": "Point", "coordinates": [longitude, latitude]}

            if update_data:
                db_manager.stores.update_one({"_id": current_user._id}, {"$set": update_data})
                flash("Profile updated successfully", "success")

            return redirect(url_for("store_routes.dashboard"))

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "error")
            return render_template("store/profile.html")
        except Exception:
            flash("An error occurred while updating profile. Please try again.", "error")
            return render_template("store/profile.html")

    return render_template("store/profile.html")
