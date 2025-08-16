"""
User Database Model

This module defines the User SQLModel for database operations and ORM mapping.
The model represents the users table in the database and provides the structure
for all user-related data persistence.

Model Features:
- SQLModel integration for enhanced functionality
- Comprehensive field validation and constraints
- Automatic timestamp management
- Secure password storage (hashed)
- Address and contact information fields
- Role-based access control support

Database Schema:
- Table: users (in sales schema)
- Primary Key: customer_id (auto-incrementing)
- Unique Constraints: email address
- Indexes: email (for authentication lookups)
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """
    User database model representing customer accounts in the system.
    
    This model defines the structure of the users table and provides
    the interface for all user-related database operations. It uses
    SQLModel which combines SQLAlchemy and Pydantic functionality.
    
    Table Configuration:
        - Schema: sales (business data separation)
        - Table Name: users
        - Primary Key: customer_id (auto-generated)
        
    Field Categories:
        - Identity: customer_id, first_name, last_name, email
        - Authentication: password (hashed)
        - Contact: phone
        - Address: address_line1, address_line2, city, state, postal_code, country
        - System: role, created_at, updated_at
        
    Security Features:
        - Passwords are stored as bcrypt hashes
        - Email addresses are unique across the system
        - Role-based access control support
        - Audit trail with timestamps
        
    Usage:
        - User registration and authentication
        - Profile management and updates
        - Address and contact information storage
        - Role-based permission systems
    """
    
    # Table configuration
    __tablename__ = "users"
    __table_args__ = {'schema': 'sales'}  # Organize business data in sales schema
    
    # Primary key - auto-generated unique identifier
    customer_id: Optional[int] = Field(
        default=None, 
        primary_key=True, 
        description="Unique user identifier"
    )
    
    # Personal information fields
    first_name: str = Field(
        ..., 
        nullable=False, 
        description="User's first/given name"
    )
    last_name: str = Field(
        ..., 
        nullable=False, 
        description="User's last/family name"
    )
    
    # Authentication and contact fields
    email: str = Field(
        ..., 
        nullable=False, 
        unique=True, 
        description="User's email address (unique)"
    )
    phone: Optional[str] = Field(
        default=None, 
        description="User's phone number"
    )
    
    # Security and access control
    password: str = Field(
        ..., 
        nullable=False, 
        description="Hashed user password (never stored in plain text)"
    )
    role: str = Field(
        default="customer", 
        nullable=False, 
        description="User's role in the system (default: customer)"
    )
    
    # Address information fields
    address_line1: str = Field(
        ..., 
        nullable=False, 
        description="Primary address line"
    )
    address_line2: Optional[str] = Field(
        default=None, 
        description="Secondary address line (optional)"
    )
    city: str = Field(
        ..., 
        nullable=False, 
        description="City name"
    )
    state: str = Field(
        ..., 
        nullable=False, 
        description="State or province name"
    )
    postal_code: str = Field(
        ..., 
        nullable=False, 
        description="Postal or ZIP code"
    )
    country: str = Field(
        ..., 
        nullable=False, 
        description="Country name"
    )
    
    # System audit fields
    created_at: Optional[datetime] = Field(
        default=None, 
        nullable=False, 
        description="Account creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None, 
        nullable=False, 
        description="Last update timestamp"
    )
    
    class Config:
        """
        SQLModel configuration for the User model.
        
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
                "customer_id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "password": "hashed_password_string",
                "role": "customer",
                "address_line1": "123 Main Street",
                "address_line2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "USA",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }