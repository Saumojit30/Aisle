import asyncio
import logging
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_engine, async_session_maker, init_db
from app.db.models import User, Product, Order, CustomerProfile
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


INITIAL_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "Wireless Noise-Cancelling Headphones",
        "category": "Electronics",
        "price": 299.99,
        "inventory": 45,
        "description": "Over-ear headphones with 30-hour battery life and active noise cancellation.",
        "tags": ["audio", "wireless", "electronics"],
    },
    {
        "id": "prod_002",
        "name": "Ergonomic Mechanical Keyboard",
        "category": "Electronics",
        "price": 149.50,
        "inventory": 12,
        "description": "Split mechanical keyboard with tactile brown switches and RGB backlighting.",
        "tags": ["keyboard", "office", "electronics"],
    },
    {
        "id": "prod_003",
        "name": "Organic Green Tea Blend",
        "category": "Groceries",
        "price": 18.00,
        "inventory": 120,
        "description": "Premium organic loose-leaf green tea sourced directly from Kyoto.",
        "tags": ["tea", "organic", "beverage"],
    },
    {
        "id": "prod_004",
        "name": "Stainless Steel Water Bottle",
        "category": "Fitness",
        "price": 34.99,
        "inventory": 80,
        "description": "Vacuum-insulated 32oz water bottle that keeps drinks cold for 24 hours.",
        "tags": ["fitness", "water", "outdoors"],
    },
    {
        "id": "prod_005",
        "name": "Smart Fitness Tracker Watch",
        "category": "Electronics",
        "price": 199.00,
        "inventory": 30,
        "description": "Heart-rate monitoring, GPS tracking, and sleep analysis smartwatch.",
        "tags": ["fitness", "watch", "smartwatch"],
    },
]


INITIAL_ORDERS = [
    {
        "id": "ord_1001",
        "customer_id": "cust_123",
        "status": "shipped",
        "items": [
            {"product_id": "prod_001", "name": "Wireless Noise-Cancelling Headphones", "quantity": 1, "price": 299.99}
        ],
        "total": 299.99,
        "tracking_number": "TRK-987654321",
    },
    {
        "id": "ord_1002",
        "customer_id": "cust_123",
        "status": "processing",
        "items": [
            {"product_id": "prod_003", "name": "Organic Green Tea Blend", "quantity": 2, "price": 18.00}
        ],
        "total": 36.00,
        "tracking_number": None,
    },
    {
        "id": "ord_1003",
        "customer_id": "cust_456",
        "status": "delivered",
        "items": [
            {"product_id": "prod_004", "name": "Stainless Steel Water Bottle", "quantity": 1, "price": 34.99}
        ],
        "total": 34.99,
        "tracking_number": "TRK-112233445",
    },
]


async def seed_data():
    await init_db()

    async with async_session_maker() as session:
        # Check if products already exist
        res = await session.execute(select(Product))
        existing_products = res.scalars().all()
        if not existing_products:
            logger.info("Seeding products...")
            for p_data in INITIAL_PRODUCTS:
                session.add(Product(**p_data))

        # Check if orders already exist
        res = await session.execute(select(Order))
        existing_orders = res.scalars().all()
        if not existing_orders:
            logger.info("Seeding orders...")
            for o_data in INITIAL_ORDERS:
                session.add(Order(**o_data))

        # Check if users exist
        res = await session.execute(select(User))
        existing_users = res.scalars().all()
        if not existing_users:
            logger.info("Seeding users & customer profiles...")
            # Demo Customer
            cust_user = User(
                id="usr_cust_123",
                email="customer@example.com",
                hashed_password=pwd_context.hash("password123"),
                role="customer",
            )
            session.add(cust_user)
            session.add(
                CustomerProfile(
                    user_id="cust_123",
                    preferences={"category": "Electronics", "brand": "Audio"},
                    interests=["headphones", "sound quality"],
                    interaction_count=3,
                )
            )

            # Demo Admin
            admin_user = User(
                id="usr_admin_999",
                email="admin@aisle.com",
                hashed_password=pwd_context.hash("admin123"),
                role="admin",
            )
            session.add(admin_user)

        await session.commit()
        logger.info("Database seeding complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_data())
