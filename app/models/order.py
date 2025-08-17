from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = {'schema': 'sales'}

    order_item_id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="sales.orders.order_id", nullable=False)
    product_id: int = Field(foreign_key="sales.products.product_id", nullable=False)
    quantity: int = Field(nullable=False)
    unit_price: Decimal = Field(nullable=False, max_digits=10, decimal_places=2)
    subtotal: Decimal = Field(nullable=False, max_digits=10, decimal_places=2)

    # Relationships
    order: Optional["Order"] = Relationship(back_populates="order_items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = {'schema': 'sales'}

    order_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="sales.users.user_id", nullable=False)
    order_date: Optional[datetime] = Field(default=None, nullable=False)
    status: str = Field(default="pending", nullable=False)
    total_amount: Decimal = Field(nullable=False, max_digits=10, decimal_places=2)
    shipping_address_line1: str = Field(nullable=False)
    shipping_address_line2: Optional[str] = None
    shipping_city: str = Field(nullable=False)
    shipping_state: str = Field(nullable=False)
    shipping_postal_code: str = Field(nullable=False)
    shipping_country: str = Field(nullable=False)

    # Relationships
    order_items: Optional[List[OrderItem]] = Relationship(back_populates="order")
