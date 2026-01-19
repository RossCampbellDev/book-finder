#!/usr/bin/env python3
"""
Seed script to populate the database with test data.

Run this script from within the web container:
    docker exec -it bookfinder-web python seed_data.py

Or run locally if you have the dependencies:
    python seed_data.py
"""
import os
import sys
from datetime import datetime
import bcrypt

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.models import Store, Book, Inventory, SearchIndex
from app.utils.database import db_manager


def create_test_stores():
    """Create test bookstore data."""
    print("Creating test stores...")

    stores_data = [
        {
            "name": "The Book Nook",
            "email": "booknook@example.com",
            "password": "password123",
            "store_type": "bookstore",
            "address": "42 Deansgate, Manchester M3 2BA",
            "latitude": 53.4808,
            "longitude": -2.2426,
            "hours": "Mon-Sat 9AM-8PM, Sun 10AM-6PM",
            "contact": "0161 555 0101",
            "website": "https://booknook.example.com"
        },
        {
            "name": "City Library",
            "email": "citylibrary@example.com",
            "password": "password123",
            "store_type": "library",
            "address": "The Headrow, Leeds LS1 3AB",
            "latitude": 53.8008,
            "longitude": -1.5491,
            "hours": "Mon-Fri 8AM-9PM, Sat-Sun 10AM-6PM",
            "contact": "0113 555 0102",
            "website": "https://citylibrary.example.com"
        },
        {
            "name": "Second Hand Stories",
            "email": "secondhand@example.com",
            "password": "password123",
            "store_type": "thrift",
            "address": "Bold Street, Liverpool L1 4JA",
            "latitude": 53.4048,
            "longitude": -2.9814,
            "hours": "Mon-Sun 10AM-7PM",
            "contact": "0151 555 0103",
            "website": None
        },
        {
            "name": "Academic Book Store",
            "email": "academic@example.com",
            "password": "password123",
            "store_type": "bookstore",
            "address": "Percy Street, Newcastle upon Tyne NE1 7RY",
            "latitude": 54.9783,
            "longitude": -1.6178,
            "hours": "Mon-Fri 9AM-6PM",
            "contact": "0191 555 0104",
            "website": "https://academicbooks.example.com"
        }
    ]

    created_stores = []
    for store_data in stores_data:
        # Check if store already exists
        existing = db_manager.stores.find_one({"email": store_data["email"]})
        if existing:
            print(f"  ✓ Store '{store_data['name']}' already exists")
            created_stores.append(Store.from_dict(existing))
            continue

        # Hash password
        password_hash = bcrypt.hashpw(store_data["password"].encode("utf-8"), bcrypt.gensalt())

        # Create store
        store = Store(
            name=store_data["name"],
            email=store_data["email"],
            password_hash=password_hash,
            store_type=store_data["store_type"],
            address=store_data["address"],
            latitude=store_data["latitude"],
            longitude=store_data["longitude"],
            hours=store_data["hours"],
            contact=store_data["contact"],
            website=store_data["website"]
        )

        result = db_manager.stores.insert_one(store.to_dict())
        store._id = result.inserted_id
        created_stores.append(store)
        print(f"  ✓ Created store: {store.name}")

    return created_stores


def create_test_books():
    """Create test book data."""
    print("\nCreating test books...")

    books_data = [
        {
            "isbn": "978-0-06-112008-4",
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "cover_url": None
        },
        {
            "isbn": "978-0-14-028329-5",
            "title": "1984",
            "author": "George Orwell",
            "cover_url": None
        },
        {
            "isbn": "978-0-7432-7356-5",
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "cover_url": None
        },
        {
            "isbn": "978-0-452-28423-4",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "cover_url": None
        },
        {
            "isbn": "978-0-06-093546-7",
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "cover_url": None
        },
        {
            "isbn": "978-0-316-76948-0",
            "title": "The Lord of the Rings",
            "author": "J.R.R. Tolkien",
            "cover_url": None
        },
        {
            "isbn": "978-0-14-243723-0",
            "title": "Animal Farm",
            "author": "George Orwell",
            "cover_url": None
        },
        {
            "isbn": "978-0-7434-3487-1",
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "cover_url": None
        },
        {
            "isbn": "978-0-06-112241-5",
            "title": "Where the Wild Things Are",
            "author": "Maurice Sendak",
            "cover_url": None
        },
        {
            "isbn": "978-0-545-01022-1",
            "title": "Harry Potter and the Deathly Hallows",
            "author": "J.K. Rowling",
            "cover_url": None
        }
    ]

    created_books = []
    for book_data in books_data:
        # Check if book already exists
        existing = db_manager.books.find_one({"isbn": book_data["isbn"]})
        if existing:
            print(f"  ✓ Book '{book_data['title']}' already exists")
            created_books.append(Book.from_dict(existing))
            continue

        # Create book
        book = Book(
            isbn=book_data["isbn"],
            title=book_data["title"],
            author=book_data["author"],
            cover_url=book_data["cover_url"]
        )

        result = db_manager.books.insert_one(book.to_dict())
        book._id = result.inserted_id
        created_books.append(book)

        # Create search index
        search_index = SearchIndex.create_from_book(
            book_data["isbn"],
            book_data["title"],
            book_data["author"]
        )
        db_manager.search_index.insert_one(search_index.to_dict())

        print(f"  ✓ Created book: {book.title}")

    return created_books


def create_test_inventory(stores, books):
    """Create test inventory data linking stores and books."""
    print("\nCreating test inventory...")

    import random

    # Define which books each store has
    inventory_mapping = {
        0: [0, 1, 2, 3, 4, 5],  # The Book Nook has first 6 books
        1: [0, 1, 2, 6, 7],     # City Library has different selection
        2: [1, 3, 4, 8],        # Second Hand Stories has used books
        3: [2, 5, 6, 7, 9]      # Academic Book Store has academic titles
    }

    conditions = ["new", "used-like-new", "used-good", "used-fair"]

    for store_idx, book_indices in inventory_mapping.items():
        store = stores[store_idx]

        for book_idx in book_indices:
            book = books[book_idx]

            # Check if inventory already exists
            existing = db_manager.inventory.find_one({
                "store_id": store._id,
                "isbn": book.isbn
            })

            if existing:
                print(f"  ✓ Inventory for '{book.title}' at '{store.name}' already exists")
                continue

            # Random quantity and condition
            qty = random.randint(1, 10)
            condition = random.choice(conditions) if store.store_type == "thrift" else "new"

            # Create inventory
            inventory = Inventory(
                store_id=store._id,
                isbn=book.isbn,
                qty=qty,
                condition=condition,
                last_updated=datetime.utcnow()
            )

            db_manager.inventory.insert_one(inventory.to_dict())
            print(f"  ✓ Added '{book.title}' to '{store.name}' (qty: {qty}, condition: {condition})")


def main():
    """Main function to seed all test data."""
    print("=" * 60)
    print("Book Finder - Database Seeding Script")
    print("=" * 60)

    try:
        # Connect to database
        print("\nConnecting to database...")
        db_manager.connect()
        print("✓ Connected to MongoDB")

        # Create test data
        stores = create_test_stores()
        books = create_test_books()
        create_test_inventory(stores, books)

        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print(f"\nCreated/verified:")
        print(f"  - {len(stores)} stores")
        print(f"  - {len(books)} books")
        print(f"  - Inventory entries")
        print("\nTest credentials (all stores):")
        print("  Password: password123")
        print("\nStores:")
        for store in stores:
            print(f"  - {store.email} ({store.name})")

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
