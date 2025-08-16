"""
FastAPI Dependency Injection Configuration Module

This module defines all the dependency injection functions and type annotations
used throughout the application. It provides a centralized way to manage
dependencies like database sessions and service instances.

Dependencies are automatically injected by FastAPI and provide:
- Database session management
- Service layer instantiation
- Proper resource cleanup
- Type safety through annotations
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.product import ProductService
from app.services.user import UserService


# Type annotation for database session dependency
# This provides type hints for IDE support and runtime validation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_product_service(session: SessionDep) -> ProductService:
    """
    Dependency function to create and inject ProductService instances.
    
    This function creates a new ProductService instance for each request,
    ensuring proper isolation and resource management.
    
    Args:
        session (SessionDep): Database session dependency
        
    Returns:
        ProductService: Configured product service instance
        
    Note:
        Each request gets a fresh service instance with its own database session.
        This ensures thread safety and proper resource cleanup.
    """
    return ProductService(session)


# Type annotation for ProductService dependency injection
# This allows FastAPI to automatically inject the service into route handlers
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]


def get_user_service(session: SessionDep) -> UserService:
    """
    Dependency function to create and inject UserService instances.
    
    This function creates a new UserService instance for each request,
    ensuring proper isolation and resource management.
    
    Args:
        session (SessionDep): Database session dependency
        
    Returns:
        UserService: Configured user service instance
        
    Note:
        Each request gets a fresh service instance with its own database session.
        This ensures thread safety and proper resource cleanup.
    """
    return UserService(session)


# Type annotation for UserService dependency injection
# This allows FastAPI to automatically inject the service into route handlers
UserServiceDep = Annotated[UserService, Depends(get_user_service)]