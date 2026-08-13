from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: f"usr_{uuid.uuid4().hex[:12]}", primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="customer")  # "customer" or "admin"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class CustomerProfile(SQLModel, table=True):
    __tablename__ = "customer_profiles"

    id: str = Field(default_factory=lambda: f"prof_{uuid.uuid4().hex[:12]}", primary_key=True)
    user_id: str = Field(unique=True, index=True)
    preferences: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    interests: List[str] = Field(default=[], sa_column=Column(JSON))
    interaction_count: int = Field(default=0)
    last_interaction: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    category: str = Field(index=True)
    price: float
    inventory: int = Field(default=0)
    description: str
    tags: List[str] = Field(default=[], sa_column=Column(JSON))


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: str = Field(primary_key=True)
    customer_id: str = Field(index=True)
    status: str = Field(index=True)  # "processing", "shipped", "delivered", "cancelled"
    items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    total: float
    tracking_number: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class PendingApproval(SQLModel, table=True):
    __tablename__ = "pending_approvals"

    id: str = Field(default_factory=lambda: f"appr_{uuid.uuid4().hex[:12]}", primary_key=True)
    thread_id: str = Field(index=True)
    session_id: str = Field(index=True)
    customer_id: str = Field(index=True)
    action_type: str  # e.g., "cancel_order", "process_refund"
    payload: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    status: str = Field(default="pending")  # "pending", "approved", "rejected"
    reason: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
