"""
Custom Exception Classes for E-commerce REST API

This module defines application-specific exception classes that provide
meaningful error messages and proper error handling throughout the application.

Custom exceptions help with:
- Consistent error handling across the application
- Meaningful error messages for clients
- Proper HTTP status code mapping
- Logging and monitoring of specific error types
- Business logic error identification
"""


class ProductNotFoundError(Exception):
    """
    Exception raised when a requested product cannot be found.
    
    This exception is typically raised when:
    - Product ID doesn't exist in the database
    - Product has been deleted
    - Product is not accessible to the current user
    
    Attributes:
        message (str): Human-readable error message describing the issue
        
    Example:
        raise ProductNotFoundError("Product with ID 123 not found")
    """
    
    def __init__(self, message: str = "Product not found"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """
    Exception raised when a requested user cannot be found.
    
    This exception is typically raised when:
    - User ID doesn't exist in the database
    - User has been deleted
    - User is not accessible to the current user
    - Email address doesn't match any existing user
    
    Attributes:
        message (str): Human-readable error message describing the issue
        
    Example:
        raise UserNotFoundError("User with email 'john@example.com' not found")
    """
    
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsError(Exception):
    """
    Exception raised when attempting to create a user that already exists.
    
    This exception is typically raised when:
    - Email address is already registered
    - Username is already taken
    - Duplicate user creation is attempted
    
    Attributes:
        message (str): Human-readable error message describing the issue
        
    Example:
        raise UserAlreadyExistsError("User with email 'john@example.com' already exists")
    """
    
    def __init__(self, message: str = "User already exists"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    """
    Exception raised when database operations fail.
    
    This exception is typically raised when:
    - Database connection fails
    - SQL queries fail to execute
    - Transaction rollbacks occur
    - Database constraints are violated
    - Connection pool is exhausted
    
    Attributes:
        message (str): Human-readable error message describing the issue
        
    Example:
        raise DatabaseError("Failed to create product due to database constraint violation")
    """
    
    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """
    Exception raised when data validation fails.
    
    This exception is typically raised when:
    - Required fields are missing
    - Data types are incorrect
    - Field values are outside acceptable ranges
    - Business rule validations fail
    - Pydantic validation errors occur
    
    Attributes:
        message (str): Human-readable error message describing the issue
        
    Example:
        raise ValidationError("Product price must be greater than zero")
    """
    
    def __init__(self, message: str = "Data validation failed"):
        self.message = message
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """
    Exception raised when business logic rules are violated.
    
    This exception is typically raised when:
    - Business workflows are not followed
    - State transitions are invalid
    - Resource availability constraints are violated
    - Business policy violations occur
    - Workflow dependencies are not met
    
    Attributes:
        message (str): Human-readable error message describing the issue
        
    Example:
        raise BusinessLogicError("Cannot delete product with active orders")
    """
    
    def __init__(self, message: str = "Business logic rule violated"):
        self.message = message
        super().__init__(self.message)
