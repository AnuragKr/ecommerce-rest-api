"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.user import UserRole
from app.models.order import OrderStatus


# Error schemas
class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None
    errors: Optional[Dict[str, List[str]]] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""
    detail: str = "Validation error"
    errors: List[Dict[str, Any]]
