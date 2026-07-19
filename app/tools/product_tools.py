from typing import Optional
from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# In-memory product catalogue
# ---------------------------------------------------------------------------
_CATALOGUE = [
    {"id": "PROD-001", "name": "Wireless Headphones", "category": "Electronics", "price": 79.99, "stock": 45, "rating": 4.5, "tags": ["audio", "bluetooth", "wireless"]},
    {"id": "PROD-002", "name": "Running Shoes",       "category": "Footwear",   "price": 129.99, "stock": 30, "rating": 4.7, "tags": ["sports", "running", "athletic"]},
    {"id": "PROD-003", "name": "Yoga Mat",             "category": "Fitness",    "price": 34.99,  "stock": 100, "rating": 4.3, "tags": ["yoga", "fitness", "exercise"]},
    {"id": "PROD-004", "name": "Smart Watch",          "category": "Electronics","price": 249.99, "stock": 20,  "rating": 4.6, "tags": ["smartwatch", "fitness", "tech"]},
    {"id": "PROD-005", "name": "Coffee Maker",         "category": "Kitchen",    "price": 89.99,  "stock": 15,  "rating": 4.4, "tags": ["coffee", "kitchen", "brewing"]},
    {"id": "PROD-006", "name": "Hiking Backpack",      "category": "Accessories","price": 59.99,  "stock": 50,  "rating": 4.2, "tags": ["travel", "bags", "outdoor"]},
    {"id": "PROD-007", "name": "Desk Lamp",             "category": "Home",      "price": 44.99,  "stock": 35,  "rating": 4.1, "tags": ["lighting", "office", "home"]},
    {"id": "PROD-008", "name": "Bluetooth Speaker",     "category": "Electronics","price": 49.99,  "stock": 60,  "rating": 4.3, "tags": ["audio", "bluetooth", "speaker"]},
]


def _match(text: str, product: dict) -> bool:
    text = text.lower()
    if text in product["name"].lower():
        return True
    if text in product["category"].lower():
        return True
    return any(text in t for t in product.get("tags", []))


@tool
def search_catalogue(query: str, category: Optional[str] = None, max_price: Optional[float] = None) -> str:
    """Search the product catalogue. Optionally filter by category and/or max price."""
    results = [p for p in _CATALOGUE if _match(query, p)]
    if category:
        results = [r for r in results if r["category"].lower() == category.lower()]
    if max_price is not None:
        results = [r for r in results if r["price"] <= max_price]

    if not results:
        return f"No products found matching '{query}'."
    lines = [f"Found {len(results)} product(s):"]
    for p in results:
        lines.append(f"  • {p['name']} — ${p['price']:.2f} — {p['category']} (stock: {p['stock']})")
    return "\n".join(lines)


@tool
def get_product_details(product_id: str) -> str:
    """Get full details for a specific product by its ID."""
    for p in _CATALOGUE:
        if p["id"] == product_id:
            return (
                f"{p['name']}\n"
                f"Category: {p['category']}\n"
                f"Price: ${p['price']:.2f}\n"
                f"Rating: {p['rating']}/5.0\n"
                f"In stock: {p['stock']}\n"
                f"Tags: {', '.join(p['tags'])}"
            )
    return f"Product '{product_id}' not found."


@tool
def check_inventory(product_id: str) -> str:
    """Check stock level for a product."""
    for p in _CATALOGUE:
        if p["id"] == product_id:
            status = "low stock" if p["stock"] < 10 else "in stock"
            return f"{p['name']}: {p['stock']} units ({status})"
    return f"Product '{product_id}' not found."
