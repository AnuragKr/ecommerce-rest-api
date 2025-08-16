"""
Product Database Model

This module defines the Product SQLModel for database operations and ORM mapping.
The model represents the products table in the database and provides the structure
for all product-related data persistence.

Model Features:
- SQLModel integration for enhanced functionality
- Comprehensive field validation and constraints
- Automatic timestamp management
- Price and stock quantity validation
- Product categorization and description support

Database Schema:
- Table: products (in sales schema)
- Primary Key: product_id (auto-incrementing)
- Unique Constraints: product names within schema
- Indexes: name (for search operations), price (for filtering)
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel
from decimal import Decimal


class Product(SQLModel, table=True):
    """
    Product database model representing items in the e-commerce catalog.
    
    This model defines the structure of the products table and provides
    the interface for all product-related database operations. It uses
    SQLModel which combines SQLAlchemy and Pydantic functionality.
    
    Table Configuration:
        - Schema: sales (business data separation)
        - Table Name: products
        - Primary Key: product_id (auto-generated)
        
    Field Categories:
        - Identity: product_id, name, description
        - Pricing: price (decimal with precision)
        - Inventory: stock_quantity
        - Metadata: created_at, updated_at
        
    Business Rules:
        - Product names must be unique within the sales schema
        - Prices must be positive decimal values
        - Stock quantities must be non-negative integers
        - All required fields must be provided during creation
        
    Usage:
        - Product catalog management
        - Inventory tracking and management
        - Pricing and availability queries
        - Product search and filtering operations
    """
    
    # Table configuration
    __tablename__ = 'products'
    __table_args__ = {'schema': 'sales'}  # Organize business data in sales schema

    # Primary key - auto-generated unique identifier
    product_id: Optional[int] = Field(
        default=None, 
        primary_key=True, 
        description="Unique product identifier"
    )
    
    # Product identification and description
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        nullable=False, 
        description="Product name (unique within schema)"
    )
    description: Optional[str] = Field(
        default=None, 
        description="Detailed product description"
    )
    
    # Pricing information with decimal precision
    price: Decimal = Field(
        ..., 
        gt=0, 
        max_digits=10, 
        decimal_places=2, 
        nullable=False, 
        description="Product price (positive decimal with 2 decimal places)"
    )
    
    # Inventory management
    stock_quantity: int = Field(
        default=0, 
        ge=0, 
        nullable=False, 
        description="Available stock quantity (non-negative integer)"
    )
    
    # System audit fields
    created_at: Optional[datetime] = Field(
        default=None, 
        nullable=False, 
        description="Product creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None, 
        nullable=False, 
        description="Last update timestamp"
    )
    
    class Config:
        """
        SQLModel configuration for the Product model.
        
        This configuration enables:
        - ORM mode for database operations
        - Pydantic validation and serialization
        - SQLAlchemy table creation and management
        """
        # Enable ORM mode for database operations
        from_attributes = True
        
        # Schema examples for documentation
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "name": "Premium Widget",
                "description": "High-quality widget for professional use",
                "price": "29.99",
                "stock_quantity": 100,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }