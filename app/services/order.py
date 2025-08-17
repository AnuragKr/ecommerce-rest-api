"""
Order Service Module

This module provides business logic layer operations for order management.
It handles order creation, validation, stock management, and all business rules
related to order operations.

The service layer sits between the API controllers and repositories,
implementing business logic, validation, and security measures.

Key Features:
- Order CRUD operations with business rule enforcement
- Stock availability validation before order placement
- Automatic stock updates after successful orders
- Comprehensive error handling and logging
- Input validation and sanitization
- Order status management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order import OrderRepository
from app.schemas.order import OrderResponse, OrderFilter, OrderCreate, OrderUpdate
from app.exceptions import OrderNotFoundError, DatabaseError, InsufficientStockError, InvalidOrderError
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

# Configure logging for order service operations
logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class for order business logic operations.
    
    This class implements all business logic related to order management,
    including validation, stock management, and business rule enforcement.
    It acts as an intermediary between the API layer and data access layer.
    
    Attributes:
        repo (OrderRepository): Repository instance for data access
        session (AsyncSession): Database session for the current operation
        
    Methods:
        create_order: Create new order with stock validation
        get_order: Retrieve order by ID with error handling
        get_user_orders: Retrieve orders for a specific user
        list_orders: Retrieve filtered list of orders
        update_order_status: Update order status with validation
        delete_order: Delete order with validation
        validate_order_items: Validate order items and calculate totals
        check_stock_availability: Check if products have sufficient stock
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize OrderService with database session.
        
        Args:
            session (AsyncSession): Database session for the service operations
        """
        self.repo = OrderRepository()
        self.session = session

    async def create_order(self, order_in: OrderCreate, user_id: int) -> OrderResponse:
        """
        Create a new order with comprehensive validation and stock management.
        
        Args:
            order_in (OrderCreate): Order creation data from API request
            user_id (int): ID of the user placing the order
            
        Returns:
            OrderResponse: Created order data
            
        Raises:
            InsufficientStockError: If any product has insufficient stock
            InvalidOrderError: If order data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate order items
            if not order_in.order_items:
                logger.warning(f"Order creation failed: no order items provided for user {user_id}")
                raise InvalidOrderError("Order must contain at least one item")
            
            # Check stock availability before creating order
            stock_available, validation_results = await self.repo.check_stock_availability(
                self.session, order_in.order_items
            )
            
            if not stock_available:
                logger.warning(f"Order creation failed: insufficient stock for user {user_id}")
                # Log detailed stock validation results
                for result in validation_results:
                    if not result['available']:
                        logger.warning(f"Stock issue: {result}")
                
                raise InsufficientStockError(
                    "Some products have insufficient stock",
                    details=validation_results
                )
            
            # Calculate order totals and prepare order items
            order_items_data = []
            total_amount = Decimal('0.00')
            
            for item in order_in.order_items:
                # Find the validation result for this item
                validation_result = next(
                    (r for r in validation_results if r['product_id'] == item['product_id']), 
                    None
                )
                
                if validation_result and validation_result['available']:
                    unit_price = validation_result['unit_price']
                    subtotal = unit_price * item['quantity']
                    total_amount += subtotal
                    
                    order_items_data.append({
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'unit_price': unit_price,
                        'subtotal': subtotal
                    })
            
            # Prepare order data
            order_data = {
                'user_id': user_id,
                'order_date': datetime.now(),
                'status': 'pending',
                'total_amount': total_amount,
                'shipping_address_line1': order_in.shipping_address_line1,
                'shipping_address_line2': order_in.shipping_address_line2,
                'shipping_city': order_in.shipping_city,
                'shipping_state': order_in.shipping_state,
                'shipping_postal_code': order_in.shipping_postal_code,
                'shipping_country': order_in.shipping_country
            }
            
            # Create order with items
            order_model = await self.repo.create_order(self.session, order_data, order_items_data)
            
            # Update product stock
            stock_updated = await self.repo.update_product_stock(self.session, order_items_data)
            if not stock_updated:
                logger.error(f"Failed to update product stock for order {order_model.order_id}")
                # Note: Order was created but stock wasn't updated - this is a critical issue
                # In production, you might want to implement compensation logic
            
            logger.info(f"Order created successfully with ID: {order_model.order_id} for user {user_id}")
            return OrderResponse.model_validate(order_model)
            
        except (InsufficientStockError, InvalidOrderError):
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to create order for user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to create order")

    async def get_order(self, order_id: int, user_id: Optional[int] = None, is_admin: bool = False) -> OrderResponse:
        """
        Retrieve an order by ID with access control.
        
        Args:
            order_id (int): ID of the order to retrieve
            user_id (Optional[int]): ID of the requesting user (for access control)
            is_admin (bool): Whether the requesting user is an admin
            
        Returns:
            OrderResponse: Order data
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            DatabaseError: If database operation fails
            PermissionError: If user doesn't have access to the order
        """
        try:
            order_model = await self.repo.get_by_id(self.session, order_id)
            if not order_model:
                logger.warning(f"Order retrieval failed: order {order_id} not found")
                raise OrderNotFoundError("Order not found")
            
            # Access control: users can only see their own orders, admins can see all
            if not is_admin and order_model.user_id != user_id:
                logger.warning(f"Access denied: user {user_id} tried to access order {order_id}")
                raise PermissionError("Access denied: you can only view your own orders")
            
            return OrderResponse.model_validate(order_model)
            
        except (OrderNotFoundError, PermissionError):
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve order {order_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve order")

    async def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 10) -> List[OrderResponse]:
        """
        Retrieve orders for a specific user with pagination.
        
        Args:
            user_id (int): ID of the user whose orders to retrieve
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            
        Returns:
            List[OrderResponse]: List of user's orders
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            order_models = await self.repo.get_by_user_id(self.session, user_id, skip, limit)
            
            if not order_models:
                logger.info(f"No orders found for user {user_id}")
                return []
            
            # Convert models to response schemas
            order_responses = [OrderResponse.model_validate(order_model) for order_model in order_models]
            logger.info(f"Retrieved {len(order_responses)} orders for user {user_id}")
            
            return order_responses
            
        except Exception as e:
            logger.error(f"Failed to retrieve orders for user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve user orders")

    async def list_orders(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        filters: OrderFilter = None,
        is_admin: bool = False
    ) -> List[OrderResponse]:
        """
        Retrieve a filtered and paginated list of orders.
        
        Args:
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (OrderFilter, optional): Filter criteria for the query
            is_admin (bool): Whether the requesting user is an admin
            
        Returns:
            List[OrderResponse]: List of orders matching the criteria
            
        Raises:
            DatabaseError: If database operation fails
            PermissionError: If non-admin user tries to access all orders
        """
        try:
            # Only admins can list all orders
            if not is_admin:
                logger.warning("Non-admin user attempted to list all orders")
                raise PermissionError("Admin privileges required to view all orders")
            
            order_models = await self.repo.get_list(self.session, skip=skip, limit=limit, filters=filters)
            
            if not order_models:
                logger.info("Order list query returned no results")
                return []
            
            # Convert models to response schemas
            order_responses = [OrderResponse.model_validate(order_model) for order_model in order_models]
            logger.info(f"Retrieved {len(order_responses)} orders successfully")
            
            return order_responses
            
        except PermissionError:
            # Re-raise permission exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to list orders: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to list orders")

    async def update_order_status(self, order_id: int, status: str, is_admin: bool = False) -> OrderResponse:
        """
        Update the status of an existing order.
        
        Args:
            order_id (int): ID of the order to update
            status (str): New status for the order
            is_admin (bool): Whether the requesting user is an admin
            
        Returns:
            OrderResponse: Updated order data
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            DatabaseError: If database operation fails
            PermissionError: If non-admin user tries to update order status
        """
        try:
            # Only admins can update order status
            if not is_admin:
                logger.warning("Non-admin user attempted to update order status")
                raise PermissionError("Admin privileges required to update order status")
            
            # Validate status
            valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
            if status not in valid_statuses:
                logger.warning(f"Invalid order status: {status}")
                raise InvalidOrderError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
            order_model = await self.repo.update_status(self.session, order_id, status)
            if not order_model:
                logger.warning(f"Order status update failed: order {order_id} not found")
                raise OrderNotFoundError("Order not found")
            
            logger.info(f"Order {order_id} status updated to: {status}")
            return OrderResponse.model_validate(order_model)
            
        except (OrderNotFoundError, PermissionError, InvalidOrderError):
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to update order {order_id} status: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to update order status")

    async def delete_order(self, order_id: int, user_id: Optional[int] = None, is_admin: bool = False) -> bool:
        """
        Delete an order with access control.
        
        Args:
            order_id (int): ID of the order to delete
            user_id (Optional[int]): ID of the requesting user (for access control)
            is_admin (bool): Whether the requesting user is an admin
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            DatabaseError: If database operation fails
            PermissionError: If user doesn't have permission to delete the order
        """
        try:
            # Get order to check access control
            order_model = await self.repo.get_by_id(self.session, order_id)
            if not order_model:
                logger.warning(f"Order deletion failed: order {order_id} not found")
                raise OrderNotFoundError("Order not found")
            
            # Access control: users can only delete their own pending orders, admins can delete any
            if not is_admin:
                if order_model.user_id != user_id:
                    logger.warning(f"Access denied: user {user_id} tried to delete order {order_id}")
                    raise PermissionError("Access denied: you can only delete your own orders")
                
                if order_model.status != 'pending':
                    logger.warning(f"Order deletion denied: order {order_id} is not pending")
                    raise PermissionError("Only pending orders can be deleted")
            
            deleted = await self.repo.delete_order(self.session, order_id)
            if deleted:
                logger.info(f"Order {order_id} deleted successfully")
            
            return deleted
            
        except (OrderNotFoundError, PermissionError):
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to delete order {order_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to delete order")

    async def get_order_statistics(self, user_id: int) -> dict:
        """
        Get order statistics for a specific user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            dict: Order statistics including count and total amount
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            order_count = await self.repo.get_order_count_by_user(self.session, user_id)
            total_sales = await self.repo.get_total_sales_by_user(self.session, user_id)
            
            return {
                'order_count': order_count,
                'total_sales': float(total_sales),
                'average_order_value': float(total_sales / order_count) if order_count > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get order statistics for user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to get order statistics")

    async def get_stock_health_info(self) -> dict:
        """
        Get comprehensive stock health information for admin dashboard.
        
        This method provides administrators with detailed insights into:
        - Products with available stock
        - Low stock alerts
        - Stock distribution statistics
        - Inventory health metrics
        
        Returns:
            dict: Comprehensive stock health information
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            stock_info = await self.repo.get_stock_health_info(self.session)
            
            # Calculate additional metrics
            total_products = len(stock_info['all_products'])
            products_with_stock = len(stock_info['products_with_stock'])
            products_low_stock = len(stock_info['low_stock_products'])
            products_out_of_stock = len(stock_info['out_of_stock_products'])
            
            # Calculate stock health percentage
            stock_health_percentage = (products_with_stock / total_products * 100) if total_products > 0 else 0
            
            return {
                'summary': {
                    'total_products': total_products,
                    'products_with_stock': products_with_stock,
                    'products_low_stock': products_low_stock,
                    'products_out_of_stock': products_out_of_stock,
                    'stock_health_percentage': round(stock_health_percentage, 2)
                },
                'stock_categories': {
                    'available_stock': stock_info['products_with_stock'],
                    'low_stock': stock_info['low_stock_products'],
                    'out_of_stock': stock_info['out_of_stock_products']
                },
                'stock_distribution': {
                    'high_stock': stock_info['high_stock_products'],
                    'medium_stock': stock_info['medium_stock_products'],
                    'critical_stock': stock_info['critical_stock_products']
                },
                'alerts': {
                    'low_stock_alerts': products_low_stock,
                    'out_of_stock_alerts': products_out_of_stock,
                    'critical_stock_alerts': len(stock_info['critical_stock_products'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get stock health info: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to get stock health information")

    async def filter_stock_info(self, stock_info: dict, category: Optional[str] = None, min_stock: Optional[int] = None, max_stock: Optional[int] = None) -> dict:
        """
        Filter stock information based on provided criteria.
        
        Args:
            stock_info (dict): Complete stock information
            category (Optional[str]): Stock category filter
            min_stock (Optional[int]): Minimum stock quantity filter
            max_stock (Optional[int]): Maximum stock quantity filter
            
        Returns:
            dict: Filtered stock information
        """
        try:
            filtered_info = stock_info.copy()
            
            # Apply category filter
            if category:
                category_mapping = {
                    'available': 'products_with_stock',
                    'low': 'low_stock_products',
                    'out_of_stock': 'out_of_stock_products',
                    'critical': 'critical_stock_products',
                    'high': 'high_stock_products',
                    'medium': 'medium_stock_products'
                }
                
                if category in category_mapping:
                    # Only return the specified category
                    for key in ['products_with_stock', 'low_stock_products', 'out_of_stock_products', 
                               'high_stock_products', 'medium_stock_products', 'critical_stock_products']:
                        if key != category_mapping[category]:
                            filtered_info[key] = []
            
            # Apply stock quantity filters
            if min_stock is not None or max_stock is not None:
                for key in ['products_with_stock', 'low_stock_products', 'high_stock_products', 
                           'medium_stock_products', 'critical_stock_products']:
                    if key in filtered_info:
                        filtered_info[key] = [
                            product for product in filtered_info[key]
                            if (min_stock is None or product['stock_quantity'] >= min_stock) and
                               (max_stock is None or product['stock_quantity'] <= max_stock)
                        ]
            
            # Update statistics based on filtered data
            total_products = len(filtered_info['all_products'])
            products_with_stock = len(filtered_info['products_with_stock'])
            products_low_stock = len(filtered_info['low_stock_products'])
            products_out_of_stock = len(filtered_info['out_of_stock_products'])
            
            # Recalculate stock health percentage
            stock_health_percentage = (products_with_stock / total_products * 100) if total_products > 0 else 0
            
            # Update summary
            filtered_info['summary'] = {
                'total_products': total_products,
                'products_with_stock': products_with_stock,
                'products_low_stock': products_low_stock,
                'products_out_of_stock': products_out_of_stock,
                'stock_health_percentage': round(stock_health_percentage, 2)
            }
            
            return filtered_info
            
        except Exception as e:
            logger.error(f"Failed to filter stock info: {str(e)}", exc_info=True)
            # Return original stock info if filtering fails
            return stock_info
