from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderItemBase(BaseModel):
    product_id: int = Field(..., description="Product ID to order")
    quantity: int = Field(..., gt=0, description="Quantity to order (must be positive)")


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    order_item_id: int
    unit_price: Decimal = Field(..., description="Unit price at time of order")
    subtotal: Decimal = Field(..., description="Total price for this item")

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    shipping_address_line1: str = Field(..., description="Primary shipping address line")
    shipping_address_line2: Optional[str] = Field(None, description="Secondary shipping address line")
    shipping_city: str = Field(..., description="Shipping city")
    shipping_state: str = Field(..., description="Shipping state/province")
    shipping_postal_code: str = Field(..., description="Shipping postal/ZIP code")
    shipping_country: str = Field(..., description="Shipping country")


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = Field(..., min_items=1, description="List of items to order")


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, description="New order status")
    shipping_address_line1: Optional[str] = Field(None, description="Primary shipping address line")
    shipping_address_line2: Optional[str] = Field(None, description="Secondary shipping address line")
    shipping_city: Optional[str] = Field(None, description="Shipping city")
    shipping_state: Optional[str] = Field(None, description="Shipping state/province")
    shipping_postal_code: Optional[str] = Field(None, description="Shipping postal/ZIP code")
    shipping_country: Optional[str] = Field(None, description="Shipping country")


class OrderResponse(OrderBase):
    order_id: int = Field(..., description="Unique order identifier")
    user_id: int = Field(..., description="User who placed the order")
    order_date: datetime = Field(..., description="Order creation timestamp")
    status: str = Field(..., description="Current order status")
    total_amount: Decimal = Field(..., description="Total order amount")
    order_items: List[OrderItemResponse] = Field(..., description="Order items")

    class Config:
        from_attributes = True


class OrderFilter(BaseModel):
    status: Optional[str] = Field(None, description="Filter by order status")
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Filter by minimum order amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Filter by maximum order amount")
