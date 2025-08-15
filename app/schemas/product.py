"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Product schemas
class ProductBase(BaseModel):
    """Base product schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode for this schema


class ProductCreate(BaseModel):
    """Product creation schema - timestamps set automatically."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    """Product update schema - allows partial updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True  # Enable ORM mode for this schema


class ProductResponse(ProductBase):
    """Product response schema."""
    product_id: int

    class Config:
        from_attributes = True  # Enable ORM mode for this schema
    


class ProductFilter(BaseModel):
    """Product filtering schema."""
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    in_stock_only: bool = False
    search: Optional[str] = None
