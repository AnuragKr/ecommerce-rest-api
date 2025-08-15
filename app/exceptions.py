"""
Custom exceptions for the ecommerce REST API.
"""

class ProductNotFoundError(Exception):
    """Exception raised when a product is not found."""
    
    def __init__(self, message: str = "Product not found"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    """Exception raised when a database operation fails."""
    
    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Exception raised when data validation fails."""
    
    def __init__(self, message: str = "Data validation failed"):
        self.message = message
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Exception raised when business logic rules are violated."""
    
    def __init__(self, message: str = "Business logic rule violated"):
        self.message = message
        super().__init__(self.message)
