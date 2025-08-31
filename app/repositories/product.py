"""
Product Repository Module

This module provides data access layer operations for product management.
It handles all database interactions related to products including CRUD operations,
search functionality, and data filtering.

The repository pattern separates data access logic from business logic,
making the code more maintainable and testable.

Key Features:
- Product CRUD operations with optimized queries
- Advanced filtering and search capabilities
- Pagination support for large datasets
- Efficient database query construction
- Proper error handling and transaction management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.product import Product
from app.models.order import OrderItem
from app.schemas.product import ProductFilter


class ProductRepository:
    """
    Repository class for product data access operations.
    
    This class encapsulates all database operations related to products,
    providing a clean interface for the service layer to interact with
    the database without exposing SQL details.
    
    Attributes:
        None - Stateless repository pattern
        
    Methods:
        get_by_id: Retrieve product by primary key
        get_list: Retrieve filtered list of products with pagination
        create: Create new product record
        update: Update existing product record
        delete: Delete product record
        
    Design Patterns:
        - Repository Pattern: Separates data access from business logic
        - Async/Await: Non-blocking database operations
        - Query Builder: Dynamic query construction based on filters
    """
    
    async def get_by_id(self, db: AsyncSession, product_id: int) -> Product:
        """
        Retrieve a product by its unique identifier.
        
        Args:
            db (AsyncSession): Database session for the operation
            product_id (int): Primary key of the product to retrieve
            
        Returns:
            Product: Product model instance if found, None otherwise
            
        Note:
            This method uses the product_id field as the primary key
            for product identification. Returns None if no product
            is found with the specified ID.
        """
        result = await db.execute(select(Product).where(Product.product_id == product_id))
        return result.scalar_one_or_none()

    async def get_list(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10, 
        filters: ProductFilter = None
    ) -> list[Product]:
        """
        Retrieve a filtered and paginated list of products.
        
        This method supports complex filtering with multiple criteria and
        provides efficient pagination for large product catalogs.
        
        Args:
            db (AsyncSession): Database session for the operation
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (ProductFilter, optional): Filter criteria for the query
            
        Returns:
            list[Product]: List of product model instances matching the criteria
            
        Filter Options:
            - price_min: Minimum price filter (inclusive)
            - price_max: Maximum price filter (inclusive)
            - in_stock_only: Filter for products with stock > 0
            - search: Text search across product name (case-insensitive)
            
        Note:
            - Pagination is handled through skip/limit parameters
            - Filters are applied using AND logic (all conditions must match)
            - Search filter performs case-insensitive partial matching
            - Empty result sets return an empty list, not None
            - Price filters support decimal precision for accurate filtering
        """
        # Start with base query for all products
        query = select(Product)
        conditions = []
        
        # Apply filters if provided
        if filters:
            # Price range filtering (inclusive bounds)
            if filters.price_min is not None:
                conditions.append(Product.price >= filters.price_min)
            if filters.price_max is not None:
                conditions.append(Product.price <= filters.price_max)
            
            # Stock availability filtering
            if filters.in_stock_only:
                conditions.append(Product.stock_quantity > 0)
            
            # Text search across product names
            if filters.search:
                conditions.append(Product.name.ilike(f"%{filters.search}%"))
        
        # Apply all conditions if any exist
        if conditions:
            query = query.where(and_(*conditions))
        
        # Execute query with pagination
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, create_data: dict) -> Product:
        """
        Create a new product record in the database.
        
        Args:
            db (AsyncSession): Database session for the operation
            create_data (dict): Dictionary containing product data for creation
            
        Returns:
            Product: Created product model instance with generated ID
            
        Note:
            - The product object is automatically added to the session
            - Changes are committed to the database
            - The object is refreshed to include generated values (e.g., ID)
            - Timestamps are typically set by the service layer
        """
        db_obj = Product(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, product_id: int, update_data: dict) -> Product:
        """
        Update an existing product record in the database.
        
        Args:
            db (AsyncSession): Database session for the operation
            product_id (int): Primary key of the product to update
            update_data (dict): Dictionary containing fields to update
            
        Returns:
            Product: Updated product model instance, None if product not found
            
        Note:
            - Only provided fields are updated (partial updates supported)
            - The object is refreshed after update to reflect changes
            - Returns None if the product doesn't exist
            - Timestamps are typically managed by the service layer
        """
        db_obj = await self.get_by_id(db, product_id)
        if not db_obj:
            return None
        
        # Update only the fields provided in update_data
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, product_id: int) -> bool:
        """
        Delete a product record from the database only if it's not present in any orders.
        
        This method performs a safety check to ensure that products with existing
        order history are not accidentally deleted, maintaining data integrity.
        
        Args:
            db (AsyncSession): Database session for the operation
            product_id (int): Primary key of the product to delete
            
        Returns:
            bool: True if deletion was successful, False if product not found or has orders
            
        Note:
            - This operation is irreversible
            - Returns False if the product doesn't exist
            - Returns False if the product is present in any order items
            - Only deletes products that have no order history
            - Consider soft deletes for production systems
        """
        # Check if product exists
        db_obj = await self.get_by_id(db, product_id)
        if not db_obj:
            return False
        
        # Check if product is present in any order items
        order_items_result = await db.execute(
            select(OrderItem).where(OrderItem.product_id == product_id)
        )
        existing_order_items = order_items_result.scalars().all()
        
        # If product has order history, don't delete it
        if existing_order_items:
            return False
        
        # Product has no order history, safe to delete
        await db.delete(db_obj)
        await db.commit()
        return True
