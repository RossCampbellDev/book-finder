"""Search functionality routes."""
from flask import Blueprint, request, jsonify, render_template
from typing import List, Dict, Any

from app.models import SearchIndex
from app.utils.database import db_manager

search_bp = Blueprint("search_routes", __name__)


@search_bp.route("/")
def search():
    """Search for books by ISBN, title, or author.

    Query parameters:
        q: Search query
        type: Search type ('isbn', 'title', 'author', 'all')
        lat: User latitude for proximity search (optional)
        lng: User longitude for proximity search (optional)
        max_distance: Maximum distance in meters (optional, default 50000)

    Returns:
        JSON response with search results
    """
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "all")
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    max_distance = request.args.get("max_distance", type=int, default=50000)

    if not query:
        return jsonify({"results": [], "message": "No search query provided"})

    results = []

    if search_type == "isbn" or search_type == "all":
        # Direct ISBN search
        book = db_manager.books.find_one({"isbn": query})
        if book:
            results.append(book)

    if search_type in ["title", "author", "all"]:
        # Tokenize search query
        tokens = SearchIndex.tokenize(query)

        # Build search query
        search_conditions = []

        if search_type == "title" or search_type == "all":
            search_conditions.append({"title_tokens": {"$in": tokens}})

        if search_type == "author" or search_type == "all":
            search_conditions.append({"author_tokens": {"$in": tokens}})

        if search_conditions:
            # Search in search index
            search_query = {"$or": search_conditions} if len(search_conditions) > 1 else search_conditions[0]
            search_results = db_manager.search_index.find(search_query)

            # Get book details for search results
            isbns = [result["isbn"] for result in search_results]
            books = db_manager.books.find({"isbn": {"$in": isbns}})

            for book in books:
                if book not in results:
                    results.append(book)

    # For each book, find stores with inventory
    enhanced_results = []
    for book in results:
        # Find inventory with quantity > 0
        inventory_query = {"isbn": book["isbn"], "qty": {"$gt": 0}}
        inventory_items = list(db_manager.inventory.find(inventory_query))

        if not inventory_items:
            continue

        # Get store details for each inventory item
        stores_with_inventory = []
        store_ids = [inv["store_id"] for inv in inventory_items]

        # Build store query with optional geospatial filter
        store_query = {"_id": {"$in": store_ids}}

        if lat is not None and lng is not None:
            # Geospatial query for nearby stores
            store_query["location"] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": max_distance
                }
            }

        stores = db_manager.stores.find(store_query)

        for store in stores:
            # Find inventory for this store
            store_inventory = next(
                (inv for inv in inventory_items if inv["store_id"] == store["_id"]),
                None
            )

            if store_inventory:
                stores_with_inventory.append({
                    "store_id": str(store["_id"]),
                    "store_name": store["name"],
                    "store_type": store.get("type", "bookstore"),
                    "address": store["address"],
                    "location": store.get("location", {}),
                    "hours": store["hours"],
                    "contact": store["contact"],
                    "website": store.get("website"),
                    "qty": store_inventory["qty"],
                    "condition": store_inventory["condition"],
                })

        if stores_with_inventory:
            enhanced_results.append({
                "isbn": book["isbn"],
                "title": book["title"],
                "author": book["author"],
                "cover_url": book.get("cover_url"),
                "stores": stores_with_inventory,
            })

    return jsonify({
        "results": enhanced_results,
        "count": len(enhanced_results),
        "query": query,
        "search_type": search_type,
    })


@search_bp.route("/autocomplete")
def autocomplete():
    """Autocomplete suggestions for book search.

    Query parameters:
        q: Partial search query
        limit: Maximum number of suggestions (default 10)

    Returns:
        JSON response with autocomplete suggestions
    """
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", type=int, default=10)

    if not query or len(query) < 2:
        return jsonify({"suggestions": []})

    # Tokenize query
    tokens = SearchIndex.tokenize(query)

    # Search for matching books
    search_results = db_manager.search_index.find(
        {
            "$or": [
                {"title_tokens": {"$in": tokens}},
                {"author_tokens": {"$in": tokens}}
            ]
        }
    ).limit(limit)

    # Get book details
    isbns = [result["isbn"] for result in search_results]
    books = list(db_manager.books.find({"isbn": {"$in": isbns}}).limit(limit))

    suggestions = [
        {
            "isbn": book["isbn"],
            "title": book["title"],
            "author": book["author"],
        }
        for book in books
    ]

    return jsonify({"suggestions": suggestions})
