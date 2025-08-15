"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.user import UserRole
from app.models.order import OrderStatus




# Authentication schemas
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scopes: List[str]


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None
    scopes: List[str] = []


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str
    scopes: Optional[List[str]] = []


