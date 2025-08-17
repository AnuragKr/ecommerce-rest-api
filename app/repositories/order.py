"""
Order Repository Module

This module provides data access layer operations for order management.
It handles all database interactions related to orders including CRUD operations,
stock validation, and order status management.

The repository pattern separates data access logic from business logic,
making the code more maintainable and testable.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderFilter
from typing import List, Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class OrderRepository:
    """
    Repository class for order data access operations.
    
    This class encapsulates all database operations related to orders,
    providing a clean interface for the service layer to interact with
    the database without exposing SQL details.
    
    Attributes:
        None - Stateless repository pattern
        
    Methods:
        create_order: Create new order with items and stock validation
        get_by_id: Retrieve order by primary key
        get_by_user_id: Retrieve orders for a specific user
        get_list: Retrieve filtered list of orders with pagination
        update_status: Update order status
        delete_order: Delete order record
        check_stock_availability: Validate product stock for order items
        update_product_stock: Update product stock after order placement
        get_order_with_items: Get order with all related items
    """
    
    async def create_order(self, db: AsyncSession, order_data: dict, order_items: List[dict]) -> Order:
        """
        Create a new order with items in a transaction.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_data (dict): Order creation data
            order_items (List[dict]): List of order items
            
        Returns:
            Order: Created order model instance with generated ID
            
        Note:
            - Creates order and order items in a single transaction
            - Updates product stock quantities
            - Handles rollback on failure
        """
        try:
            # Create order
            db_order = Order(**order_data)
            db.add(db_order)
            await db.flush()  # Get the order_id without committing
            
            # Create order items
            for item_data in order_items:
                item_data['order_id'] = db_order.order_id
                db_order_item = OrderItem(**item_data)
                db.add(db_order_item)
            
            await db.commit()
            await db.refresh(db_order)
            return db_order
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create order: {str(e)}")
            raise
    
    async def get_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        """
        Retrieve an order by their unique identifier.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_id (int): Primary key of the order to retrieve
            
        Returns:
            Order: Order model instance if found, None otherwise
        """
        result = await db.execute(
            select(Order)
            .where(Order.order_id == order_id)
            .options(selectinload(Order.order_items))
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
        """
        Retrieve orders for a specific user with pagination.
        
        Args:
            db (AsyncSession): Database session for the operation
            user_id (int): ID of the user whose orders to retrieve
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            
        Returns:
            List[Order]: List of order model instances for the user
        """
        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(Order.order_items))
        )
        return result.scalars().all()
    
    async def get_list(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10, 
        filters: OrderFilter = None
    ) -> List[Order]:
        """
        Retrieve a filtered and paginated list of orders.
        
        Args:
            db (AsyncSession): Database session for the operation
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (OrderFilter, optional): Filter criteria for the query
            
        Returns:
            List[Order]: List of order model instances matching the criteria
        """
        query = select(Order).options(selectinload(Order.order_items))
        conditions = []
        
        # Apply filters if provided
        if filters:
            if filters.status:
                conditions.append(Order.status == filters.status)
            
            if filters.user_id:
                conditions.append(Order.user_id == filters.user_id)
            
            if filters.start_date:
                conditions.append(Order.order_date >= filters.start_date)
            
            if filters.end_date:
                conditions.append(Order.order_date <= filters.end_date)
            
            if filters.min_amount:
                conditions.append(Order.total_amount >= filters.min_amount)
            
            if filters.max_amount:
                conditions.append(Order.total_amount <= filters.max_amount)
        
        # Apply all conditions if any exist
        if conditions:
            query = query.where(and_(*conditions))
        
        # Execute query with pagination and ordering
        result = await db.execute(
            query.order_by(Order.order_date.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update_status(self, db: AsyncSession, order_id: int, status: str) -> Optional[Order]:
        """
        Update the status of an existing order.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_id (int): Primary key of the order to update
            status (str): New status for the order
            
        Returns:
            Order: Updated order model instance, None if order not found
        """
        db_order = await self.get_by_id(db, order_id)
        if not db_order:
            return None
        
        db_order.status = status
        await db.commit()
        await db.refresh(db_order)
        return db_order
    
    async def delete_order(self, db: AsyncSession, order_id: int) -> bool:
        """
        Delete an order record from the database.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_id (int): Primary key of the order to delete
            
        Returns:
            bool: True if deletion was successful, False if order not found
            
        Note:
            - This operation is irreversible
            - Consider soft deletes for production systems
        """
        db_order = await self.get_by_id(db, order_id)
        if not db_order:
            return False
        
        await db.delete(db_order)
        await db.commit()
        return True
    
    async def check_stock_availability(self, db: AsyncSession, order_items: List[dict]) -> Tuple[bool, List[dict]]:
        """
        Check if all products in order items have sufficient stock.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_items (List[dict]): List of order items to validate
            
        Returns:
            Tuple[bool, List[dict]]: (is_available, validation_results)
                - is_available: True if all items have sufficient stock
                - validation_results: List of validation results for each item
        """
        validation_results = []
        all_available = True
        
        for item in order_items:
            product_id = item['product_id']
            requested_quantity = item['quantity']
            
            # Get product stock
            result = await db.execute(
                select(Product.stock_quantity, Product.price, Product.name)
                .where(Product.product_id == product_id)
            )
            product_data = result.scalar_one_or_none()
            
            if not product_data:
                validation_results.append({
                    'product_id': product_id,
                    'available': False,
                    'error': 'Product not found'
                })
                all_available = False
                continue
            
            stock_quantity, price, name = product_data
            
            if stock_quantity < requested_quantity:
                validation_results.append({
                    'product_id': product_id,
                    'product_name': name,
                    'requested': requested_quantity,
                    'available': stock_quantity,
                    'available': False,
                    'error': f'Insufficient stock. Available: {stock_quantity}, Requested: {requested_quantity}'
                })
                all_available = False
            else:
                validation_results.append({
                    'product_id': product_id,
                    'product_name': name,
                    'requested': requested_quantity,
                    'available': stock_quantity,
                    'available': True,
                    'unit_price': price
                })
        
        return all_available, validation_results
    
    async def update_product_stock(self, db: AsyncSession, order_items: List[dict]) -> bool:
        """
        Update product stock quantities after order placement.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_items (List[dict]): List of order items with quantities
            
        Returns:
            bool: True if stock update was successful
            
        Note:
            - Reduces stock quantities by ordered amounts
            - Should be called within a transaction
        """
        try:
            for item in order_items:
                product_id = item['product_id']
                quantity = item['quantity']
                
                # Update product stock
                await db.execute(
                    update(Product)
                    .where(Product.product_id == product_id)
                    .values(stock_quantity=Product.stock_quantity - quantity)
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update product stock: {str(e)}")
            return False
    
    async def get_order_with_items(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        """
        Get order with all related items and product details.
        
        Args:
            db (AsyncSession): Database session for the operation
            order_id (int): Primary key of the order to retrieve
            
        Returns:
            Order: Order with items if found, None otherwise
        """
        result = await db.execute(
            select(Order)
            .where(Order.order_id == order_id)
            .options(selectinload(Order.order_items))
        )
        return result.scalar_one_or_none()
    
    async def get_order_count_by_user(self, db: AsyncSession, user_id: int) -> int:
        """
        Get the total count of orders for a specific user.
        
        Args:
            db (AsyncSession): Database session for the operation
            user_id (int): ID of the user
            
        Returns:
            int: Total number of orders for the user
        """
        result = await db.execute(
            select(func.count(Order.order_id))
            .where(Order.user_id == user_id)
        )
        return result.scalar()
    
    async def get_total_sales_by_user(self, db: AsyncSession, user_id: int) -> Decimal:
        """
        Get the total sales amount for a specific user.
        
        Args:
            db (AsyncSession): Database session for the operation
            user_id (int): ID of the user
            
        Returns:
            Decimal: Total sales amount for the user
        """
        result = await db.execute(
            select(func.sum(Order.total_amount))
            .where(Order.user_id == user_id)
        )
        return result.scalar() or Decimal('0.00')

    async def get_stock_health_info(self, db: AsyncSession) -> dict:
        """
        Get comprehensive stock health information for all products.
        
        This method provides detailed stock analysis including:
        - Products with available stock
        - Low stock products
        - Out of stock products
        - Stock distribution by levels
        
        Args:
            db (AsyncSession): Database session for the operation
            
        Returns:
            dict: Comprehensive stock health information
        """
        try:
            # Get all products with their stock information
            result = await db.execute(
                select(Product.product_id, Product.name, Product.stock_quantity, Product.price)
                .order_by(Product.stock_quantity.desc())
            )
            all_products = result.fetchall()
            
            # Categorize products by stock levels
            products_with_stock = []
            low_stock_products = []
            out_of_stock_products = []
            high_stock_products = []
            medium_stock_products = []
            critical_stock_products = []
            
            # Define stock thresholds
            LOW_STOCK_THRESHOLD = 10
            MEDIUM_STOCK_THRESHOLD = 50
            CRITICAL_STOCK_THRESHOLD = 5
            
            for product in all_products:
                product_id, name, stock_quantity, price = product
                product_info = {
                    'product_id': product_id,
                    'name': name,
                    'stock_quantity': stock_quantity,
                    'price': float(price),
                    'stock_value': float(price * stock_quantity)
                }
                
                # Categorize by stock availability
                if stock_quantity > 0:
                    products_with_stock.append(product_info)
                    
                    # Categorize by stock levels
                    if stock_quantity <= CRITICAL_STOCK_THRESHOLD:
                        critical_stock_products.append(product_info)
                    elif stock_quantity <= LOW_STOCK_THRESHOLD:
                        low_stock_products.append(product_info)
                    elif stock_quantity <= MEDIUM_STOCK_THRESHOLD:
                        medium_stock_products.append(product_info)
                    else:
                        high_stock_products.append(product_info)
                else:
                    out_of_stock_products.append(product_info)
            
            # Calculate stock statistics
            total_stock_value = sum(p['stock_value'] for p in products_with_stock)
            average_stock_quantity = sum(p['stock_quantity'] for p in products_with_stock) / len(products_with_stock) if products_with_stock else 0
            
            return {
                'all_products': [{'product_id': p[0], 'name': p[1], 'stock_quantity': p[2], 'price': float(p[3])} for p in all_products],
                'products_with_stock': products_with_stock,
                'low_stock_products': low_stock_products,
                'out_of_stock_products': out_of_stock_products,
                'high_stock_products': high_stock_products,
                'medium_stock_products': medium_stock_products,
                'critical_stock_products': critical_stock_products,
                'statistics': {
                    'total_stock_value': round(total_stock_value, 2),
                    'average_stock_quantity': round(average_stock_quantity, 2),
                    'total_products': len(all_products),
                    'products_with_stock': len(products_with_stock),
                    'products_out_of_stock': len(out_of_stock_products)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stock health info: {str(e)}")
            raise
