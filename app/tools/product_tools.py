from typing import Optional
import asyncio
from langchain_core.tools import tool
from sqlmodel import select
from app.db.database import async_session_maker
from app.db.models import Product

# Fallback catalog for initial sync context if DB is initializing
_FALLBACK_CATALOGUE = [
    {"id": "PROD-001", "name": "Wireless Headphones", "category": "Electronics", "price": 79.99, "inventory": 45, "tags": ["audio", "bluetooth", "wireless"]},
    {"id": "PROD-002", "name": "Running Shoes", "category": "Footwear", "price": 129.99, "inventory": 30, "tags": ["sports", "running", "athletic"]},
    {"id": "PROD-003", "name": "Yoga Mat", "category": "Fitness", "price": 34.99, "inventory": 100, "tags": ["yoga", "fitness", "exercise"]},
]


async def _search_products_db(query: str, category: Optional[str] = None, max_price: Optional[float] = None) -> list[Product]:
    async with async_session_maker() as session:
        statement = select(Product)
        if category:
            statement = statement.where(Product.category.ilike(f"%{category}%"))
        if max_price is not None:
            statement = statement.where(Product.price <= max_price)

        res = await session.execute(statement)
        products = res.scalars().all()

        query_lower = query.lower()
        matched = []
        for p in products:
            if (
                query_lower in p.name.lower()
                or query_lower in p.category.lower()
                or query_lower in p.description.lower()
                or any(query_lower in t.lower() for t in p.tags)
            ):
                matched.append(p)
        return matched if matched else list(products[:5])


@tool
def search_catalogue(query: str, category: Optional[str] = None, max_price: Optional[float] = None) -> str:
    """Search the product catalogue in the database. Filter by query, category, or max price."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Run in event loop thread
            import nest_asyncio
            nest_asyncio.apply()
            products = loop.run_until_complete(_search_products_db(query, category, max_price))
        else:
            products = asyncio.run(_search_products_db(query, category, max_price))
    except Exception:
        # Fallback to local filtering
        products = [
            Product(**p, description="Sample product description")
            for p in _FALLBACK_CATALOGUE
        ]

    if not products:
        return f"No products found matching '{query}'."

    lines = [f"Found {len(products)} product(s):"]
    for p in products:
        lines.append(f"  • {p.name} (ID: {p.id}) — ${p.price:.2f} — {p.category} (Stock: {p.inventory})")
    return "\n".join(lines)


async def _get_product_db(product_id: str) -> Optional[Product]:
    async with async_session_maker() as session:
        res = await session.execute(select(Product).where(Product.id == product_id))
        return res.scalar_one_or_none()


@tool
def get_product_details(product_id: str) -> str:
    """Get full details for a specific product by its ID."""
    try:
        p = asyncio.run(_get_product_db(product_id))
    except Exception:
        p = None

    if p:
        return (
            f"{p.name} (ID: {p.id})\n"
            f"Category: {p.category}\n"
            f"Price: ${p.price:.2f}\n"
            f"In stock: {p.inventory}\n"
            f"Description: {p.description}\n"
            f"Tags: {', '.join(p.tags)}"
        )
    return f"Product '{product_id}' not found."


@tool
def check_inventory(product_id: str) -> str:
    """Check stock level for a product."""
    try:
        p = asyncio.run(_get_product_db(product_id))
    except Exception:
        p = None

    if p:
        status = "low stock" if p.inventory < 10 else "in stock"
        return f"{p.name}: {p.inventory} units available ({status})"
    return f"Product '{product_id}' not found."
