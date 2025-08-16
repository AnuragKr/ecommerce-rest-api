"""
Product Data Schema Definitions

This module defines Pydantic models for product-related data validation,
serialization, and API documentation. The schemas ensure data integrity
and provide clear contracts between API layers.

Schema Hierarchy:
- ProductBase: Common product fields shared across all schemas
- ProductCreate: Schema for product creation requests
- ProductUpdate: Schema for product update requests (all fields optional)
- ProductResponse: Schema for product data responses
- ProductFilter: Schema for product search and filtering criteria

Key Features:
- Comprehensive field validation with meaningful constraints
- Automatic data type conversion and validation
- OpenAPI documentation generation
- ORM mode support for SQLModel integration
- Decimal precision for accurate pricing
- Stock quantity validation for inventory management
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    """
    Base product schema with common fields shared across all product operations.
    
    This schema defines the core product attributes that are consistent
    across creation, updates, and responses. It serves as the foundation
    for other product-related schemas.
    
    Attributes:
        name (str): Product name (1-200 characters)
        description (Optional[str]): Detailed product description
        price (Decimal): Product price (positive value)
        stock_quantity (int): Available stock (non-negative)
        created_at (Optional[datetime]): Product creation timestamp
        updated_at (Optional[datetime]): Last update timestamp
        
    Validation Rules:
        - name: Minimum 1 character, maximum 200 characters, required
        - price: Must be greater than 0, required
        - stock_quantity: Must be greater than or equal to 0, default 0
        - Timestamps: Automatically managed by the system
        
    Business Rules:
        - Product names should be descriptive and unique
        - Prices must be positive to prevent invalid pricing
        - Stock quantities cannot be negative
    """
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price (positive value)")
    stock_quantity: int = Field(0, ge=0, description="Available stock quantity")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        # Enable ORM mode for SQLModel integration
        from_attributes = True
        
        # Schema examples for API documentation
        json_schema_extra = {
            "example": {
                "name": "Premium Widget",
                "description": "High-quality widget for professional use",
                "price": "29.99",
                "stock_quantity": 100,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ProductCreate(BaseModel):
    """
    Schema for product creation requests.
    
    This schema defines the fields required for creating new products.
    Timestamps are automatically managed by the service layer.
    
    Attributes:
        name (str): Product name (1-200 characters)
        description (Optional[str]): Detailed product description
        price (Decimal): Product price (positive value)
        stock_quantity (int): Available stock (non-negative)
        
    Validation Rules:
        - name: Minimum 1 character, maximum 200 characters, required
        - price: Must be greater than 0, required
        - stock_quantity: Must be greater than or equal to 0, default 0
        - description: Optional field for additional product information
        
    Usage:
        - Product registration and catalog management
        - Inventory initialization
        - New product launches
    """
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price (positive value)")
    stock_quantity: int = Field(0, ge=0, description="Available stock quantity")
    
    class Config:
        # Schema examples for API documentation
        json_schema_extra = {
            "example": {
                "name": "Premium Widget",
                "description": "High-quality widget for professional use",
                "price": "29.99",
                "stock_quantity": 100
            }
        }


class ProductUpdate(BaseModel):
    """
    Schema for product update requests.
    
    This schema allows partial updates by making all fields optional.
    Only provided fields will be updated, supporting flexible product
    modifications.
    
    Attributes:
        name (Optional[str]): Product name (1-200 characters if provided)
        description (Optional[str]): Product description
        price (Optional[Decimal]): Product price (positive value if provided)
        stock_quantity (Optional[int]): Available stock (non-negative if provided)
        
    Validation Rules:
        - All fields are optional for partial updates
        - Provided fields must meet the same validation rules as ProductBase
        - name: 1-200 characters if provided
        - price: Must be greater than 0 if provided
        - stock_quantity: Must be greater than or equal to 0 if provided
        
    Update Behavior:
        - Only provided fields are updated
        - Timestamps are automatically managed
        - Validation applies only to updated fields
        - Supports incremental product modifications
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[Decimal] = Field(None, gt=0, description="Product price (positive value)")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Available stock quantity")

    class Config:
        from_attributes = True
        
        # Example for partial update
        json_schema_extra = {
            "example": {
                "price": "34.99",
                "stock_quantity": 150
            }
        }


class ProductResponse(ProductBase):
    """
    Schema for product data responses.
    
    This schema extends ProductBase and adds the product_id field for
    complete product identification. It's used for all API responses
    that return product data.
    
    Attributes:
        product_id (int): Unique identifier for the product
        
    Response Features:
        - Complete product information for display
        - Standardized response format across all endpoints
        - All public product data included
        
    Usage:
        - API responses for product retrieval
        - Product list operations
        - Product detail pages
        - Catalog and search results
    """
    product_id: int = Field(..., description="Unique product identifier")

    class Config:
        from_attributes = True
        
        # Example response data
        json_schema_extra = {
            "example": {
                "product_id": 123,
                "name": "Premium Widget",
                "description": "High-quality widget for professional use",
                "price": "29.99",
                "stock_quantity": 100,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ProductFilter(BaseModel):
    """
    Schema for product search and filtering criteria.
    
    This schema defines the parameters used for filtering product lists
    and search operations. All filters are optional and can be
    combined for more specific queries.
    
    Attributes:
        price_min (Optional[float]): Minimum price filter (inclusive)
        price_max (Optional[float]): Maximum price filter (inclusive)
        in_stock_only (bool): Filter for products with stock > 0
        search (Optional[str]): Search term for product names
        
    Filter Behavior:
        - price_min: Inclusive lower bound for price filtering
        - price_max: Inclusive upper bound for price filtering
        - in_stock_only: Boolean flag for availability filtering
        - search: Text search across product names (case-insensitive)
        - All filters use AND logic (all conditions must match)
        
    Usage:
        - Product catalog filtering
        - Price range searches
        - Stock availability queries
        - Product name searches
        - Combined filtering for advanced queries
    """
    price_min: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    price_max: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    in_stock_only: bool = Field(False, description="Filter for in-stock products only")
    search: Optional[str] = Field(None, description="Search term for product names")
    
    class Config:
        # Example filter usage
        json_schema_extra = {
            "example": {
                "price_min": 10.0,
                "price_max": 50.0,
                "in_stock_only": True,
                "search": "widget"
            }
        }
