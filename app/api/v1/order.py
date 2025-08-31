"""
Order API Controller Module

This module defines the REST API endpoints for order management operations.
It handles HTTP requests, input validation, error handling, and response
formatting for all order-related operations.

The controller layer is responsible for:
- HTTP request/response handling
- Input validation and sanitization
- Error handling and HTTP status codes
- Response formatting and serialization
- API documentation through OpenAPI schemas
- Access control and authorization

API Endpoints:
- POST /orders/ - Create new order (with stock validation)
- GET /orders/ - List orders (admin only)
- GET /orders/my-orders - List current user's orders
- GET /orders/statistics - Get overall platform statistics (admin only)
- GET /orders/user-statistics - Get user-specific statistics
- GET /orders/health/stock-check - Stock health check (admin only)
- GET /orders/{order_id} - Retrieve order by ID (access controlled)
- PUT /orders/{order_id}/status - Update order status (admin only)
- DELETE /orders/{order_id} - Delete order (access controlled)
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.dependencies import OrderServiceDep, CurrentAdminDep, CurrentCustomerDep, CurrentUserDep
from app.schemas.order import OrderCreate, OrderResponse, OrderFilter, OrderUpdate
from app.exceptions import OrderNotFoundError, DatabaseError, InsufficientStockError, InvalidOrderError, PermissionError
from typing import Annotated, List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

# Create router instance for order endpoints
router = APIRouter(prefix="/orders", tags=["orders"])


class OrderStatusUpdate(BaseModel):
    """Request model for order status updates."""
    status: str


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    service: OrderServiceDep,
    current_user: CurrentCustomerDep
):
    """
    Create a new order with comprehensive validation.
    
    This endpoint:
    - Validates all order items
    - Checks stock availability for each product
    - Prevents order creation if stock is insufficient
    - Automatically updates product stock after successful order
    - Calculates order totals based on current product prices
    
    Args:
        order (OrderCreate): Order creation data including items and shipping address
        service (OrderServiceDep): Injected order service dependency
        current_user (CurrentCustomerDep): Currently authenticated user
        
    Returns:
        OrderResponse: Created order data with all details
    """
    try:
        return await service.create_order(order, current_user.user_id)
    except InsufficientStockError as e:
        # Return detailed stock information to help user understand the issue
        raise HTTPException(
            status_code=400, 
            detail={
                "message": str(e),
                "stock_issues": getattr(e, 'details', [])
            }
        )
    except InvalidOrderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to create order at this time")


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    service: OrderServiceDep,
    current_admin: CurrentAdminDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    user_id: Optional[int] = Query(None, description="Filter by specific user"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Filter by minimum order amount"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Filter by maximum order amount"),
):
    """
    Retrieve a filtered and paginated list of all orders (Admin only).
    
    This endpoint provides comprehensive order management capabilities
    for administrators, including filtering by various criteria.
    
    Args:
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return (max 100)
        status (str, optional): Filter by order status
        user_id (int, optional): Filter by specific user
        start_date (datetime, optional): Filter by start date
        end_date (datetime, optional): Filter by end date
        min_amount (Decimal, optional): Filter by minimum order amount
        max_amount (Decimal, optional): Filter by maximum order amount
        service (OrderServiceDep): Injected order service dependency
        current_admin (CurrentAdminDep): Currently authenticated admin user
        
    Returns:
        List[OrderResponse]: List of orders matching the criteria
    """
    try:
        # Create filter object from query parameters
        filters = OrderFilter(
            status=status,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount
        )
        
        return await service.list_orders(
            skip=skip, 
            limit=limit, 
            filters=filters,
            is_admin=True
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve orders at this time")


@router.get("/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
    service: OrderServiceDep,
    current_user: CurrentCustomerDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
):
    """
    Retrieve orders for the currently authenticated user.
    
    This endpoint allows users to view their own order history
    with pagination support for better performance.
    
    Args:
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return (max 100)
        service (OrderServiceDep): Injected order service dependency
        current_user (CurrentCustomerDep): Currently authenticated user
        
    Returns:
        List[OrderResponse]: List of user's orders
    """
    try:
        return await service.get_user_orders(
            current_user.user_id, 
            skip=skip, 
            limit=limit
        )
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve your orders at this time")


@router.get("/statistics")
async def get_order_statistics(
    service: OrderServiceDep,
    current_admin: CurrentAdminDep,
):
    """
    Get comprehensive order statistics across all users (Admin only).
    
    This endpoint provides administrators with detailed insights into:
    - Total orders and sales across the platform
    - Order distribution by status
    - Top customers by order count
    - Monthly sales trends
    - Platform performance metrics
    
    Args:
        service (OrderServiceDep): Injected order service dependency
        current_admin (CurrentAdminDep): Currently authenticated admin user
        
    Returns:
        dict: Comprehensive overall order statistics
    """
    try:
        return await service.get_overall_order_statistics()
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve order statistics at this time")


@router.get("/user-statistics")
async def get_user_order_statistics(
    service: OrderServiceDep,
    current_user: CurrentCustomerDep
):
    """
    Get order statistics for the currently authenticated user.
    
    This endpoint provides users with insights into their
    ordering patterns and spending habits.
    
    Args:
        service (OrderServiceDep): Injected order service dependency
        current_user (CurrentCustomerDep): Currently authenticated user
        
    Returns:
        dict: Order statistics including count, total sales, and average order value
    """
    try:
        return await service.get_overall_order_statistics_for_user(current_user.user_id)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve order statistics at this time")


@router.get("/health/stock-check")
async def check_stock_health(
    service: OrderServiceDep,
    current_admin: CurrentAdminDep,
    category: Optional[str] = Query(None, description="Filter by stock category (available, low, out_of_stock, critical)"),
    min_stock: Optional[int] = Query(None, ge=0, description="Minimum stock quantity filter"),
    max_stock: Optional[int] = Query(None, ge=0, description="Maximum stock quantity filter")
):
    """
    Health check endpoint for stock management (Admin only).
    
    This endpoint provides administrators with a comprehensive overview
    of the stock management system including:
    - All products with available stock
    - Low stock alerts
    - Stock distribution statistics
    - System health status
    
    Args:
        service (OrderServiceDep): Injected order service dependency
        current_admin (CurrentAdminDep): Currently authenticated admin user
        
    Returns:
        dict: Comprehensive stock management system information
    """
    try:
        # Get comprehensive stock information
        stock_info = await service.get_stock_health_info()
        
        # Apply filters if provided
        filtered_stock_info = stock_info
        if category or min_stock is not None or max_stock is not None:
            filtered_stock_info = await service.filter_stock_info(stock_info, category, min_stock, max_stock)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "Stock management system is operational",
            "stock_summary": filtered_stock_info,
            "filters_applied": {
                "category": category,
                "min_stock": min_stock,
                "max_stock": max_stock
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Failed to retrieve stock health information"
        }


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    service: OrderServiceDep,
    current_user: CurrentCustomerDep
):
    """
    Retrieve an order by ID with access control.
    
    Users can only view their own orders. This ensures data privacy
    and prevents unauthorized access to order information.
    
    Args:
        order_id (int): Unique identifier of the order to retrieve
        service (OrderServiceDep): Injected order service dependency
        current_user (CurrentCustomerDep): Currently authenticated user
        
    Returns:
        OrderResponse: Order data with all details and items
    """
    try:
        return await service.get_order(
            order_id, 
            user_id=current_user.user_id, 
            is_admin=(current_user.role == "admin")
        )
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve order at this time")


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    service: OrderServiceDep,
    current_admin: CurrentAdminDep,
    order_id: int,
    status_update: OrderStatusUpdate,
):
    """
    Update the status of an existing order (Admin only).
    
    This endpoint allows administrators to manage order workflow
    by updating order statuses (pending → confirmed → shipped → delivered).
    
    Args:
        order_id (int): Unique identifier of the order to update
        status_update (OrderStatusUpdate): Request body containing the new status
        service (OrderServiceDep): Injected order service dependency
        current_admin (CurrentAdminDep): Currently authenticated admin user
        
    Returns:
        OrderResponse: Updated order data
    """
    try:
        return await service.update_order_status(order_id, status_update.status)
    except InvalidOrderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to update order status at this time")


@router.delete("/{order_id}")
async def delete_order(
    service: OrderServiceDep,
    current_user: CurrentUserDep,
    order_id: int,
):
    """
    Delete an order with access control.
    
    Users can only delete their own pending orders, while admins can delete any order. This prevents unauthorized deletions and maintains data integrity.

    Args:
        order_id (int): Unique identifier of the order to delete
        service (OrderServiceDep): Injected order service dependency
        current_user (CurrentCustomerDep): Currently authenticated user
        
    Returns:
        dict: Success message confirming deletion
    """
    try:
        deleted = await service.delete_order(
            order_id, 
            user_id=current_user.user_id, 
            is_admin=(current_user.role == "admin")
        )
        
        if deleted:
            return {"message": "Order deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Order not found")
            
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to delete order at this time")
