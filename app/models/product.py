from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel
from decimal import Decimal


class Product(SQLModel, table = True):
    __tablename__ = 'products'
    __table_args__ = {'schema': 'sales'}

    product_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, nullable=False)
    stock_quantity: int = Field(default=0, ge=0, nullable=False)
    created_at: Optional[datetime] = Field(default=None, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=False)