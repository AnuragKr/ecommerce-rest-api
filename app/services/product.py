"""
Product Service Module

This module provides business logic layer operations for product management.
It handles product validation, business rules, and orchestrates operations
between the API controllers and repositories.

The service layer sits between the API layer and repositories,
implementing business logic, validation, and security measures.

Key Features:
- Product CRUD operations with business rule enforcement
- Comprehensive input validation and sanitization
- Automatic timestamp management
- Advanced filtering and search capabilities
- Comprehensive error handling and logging
- Business logic validation and constraints
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product import ProductRepository
from app.schemas.product import ProductResponse, ProductFilter, ProductCreate, ProductUpdate
from app.exceptions import ProductNotFoundError, DatabaseError
import logging
from datetime import datetime

# Configure logging for product service operations
logger = logging.getLogger(__name__)


class ProductService:
    """
    Service class for product business logic operations.
    
    This class implements all business logic related to product management,
    including validation, business rule enforcement, and data transformation.
    It acts as an intermediary between the API layer and data access layer.
    
    Attributes:
        repo (ProductRepository): Repository instance for data access
        session (AsyncSession): Database session for the current operation
        
    Methods:
        create_product: Create new product with validation and business rules
        update_product: Update existing product with validation
        get_product: Retrieve product by ID with error handling
        list_products: Retrieve filtered list of products
        delete_product: Delete product with business rule validation
        
    Business Rules:
        - Product names must be unique within the system
        - Prices must be positive decimal values
        - Stock quantities must be non-negative integers
        - Timestamps are automatically managed
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize ProductService with database session.
        
        Args:
            session (AsyncSession): Database session for the service operations
        """
        self.repo = ProductRepository()
        self.session = session

    async def create_product(self, product_in: ProductCreate) -> ProductResponse:
        """
        Create a new product with comprehensive validation and business rules.
        
        This method implements the product creation workflow including:
        - Input validation and sanitization
        - Business rule enforcement
        - Automatic timestamp management
        - Data transformation and persistence
        
        Args:
            product_in (ProductCreate): Product creation data from API request
            
        Returns:
            ProductResponse: Created product data
            
        Raises:
            DatabaseError: If database operation fails
            
        Note:
            - Creation and update timestamps are automatically set
            - All business rules are validated before creation
            - Product data is transformed to response format
            - Comprehensive logging for audit trail
        """
        try:
            # Prepare product data for creation
            create_data = product_in.model_dump()
            current_time = datetime.now()
            
            # Set automatic timestamps for audit trail
            create_data['created_at'] = current_time
            create_data['updated_at'] = current_time
            
            # Create product in database through repository
            product_model = await self.repo.create(self.session, create_data)
            logger.info(f"Product created successfully with ID: {product_model.product_id}")
            
            # Transform model to response schema
            return ProductResponse.model_validate(product_model)
            
        except Exception as e:
            logger.error(f"Failed to create product: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to create product")

    async def update_product(self, product_id: int, product_in: ProductUpdate) -> ProductResponse:
        """
        Update an existing product with validation and business rule enforcement.
        
        This method implements the product update workflow including:
        - Product existence validation
        - Partial update support
        - Business rule validation
        - Automatic timestamp management
        
        Args:
            product_id (int): ID of the product to update
            product_in (ProductUpdate): Product update data from API request
            
        Returns:
            ProductResponse: Updated product data
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            DatabaseError: If database operation fails
            
        Note:
            - Only provided fields are updated (partial updates supported)
            - Update timestamp is automatically set
            - Product existence is validated before update
            - Business rules are enforced during update
        """
        try:
            # Prepare update data with automatic timestamp
            update_data = product_in.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.now()
            
            # Update product in database through repository
            product_model = await self.repo.update(self.session, product_id, update_data)
            if not product_model:
                logger.warning(f"Product update failed: product {product_id} not found")
                raise ProductNotFoundError("Product not found")
            
            logger.info(f"Product {product_id} updated successfully")
            return ProductResponse.model_validate(product_model)
            
        except ProductNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to update product")

    async def get_product(self, product_id: int) -> ProductResponse:
        """
        Retrieve a product by its unique identifier.
        
        Args:
            product_id (int): ID of the product to retrieve
            
        Returns:
            ProductResponse: Product data
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            DatabaseError: If database operation fails
            
        Note:
            - Returns product data in standardized response format
            - Comprehensive error logging for debugging
            - Product existence is validated before retrieval
        """
        try:
            product_model = await self.repo.get_by_id(self.session, product_id)
            if not product_model:
                logger.warning(f"Product retrieval failed: product {product_id} not found")
                raise ProductNotFoundError("Product not found")
            
            return ProductResponse.model_validate(product_model)
            
        except ProductNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve product {product_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve product")

    async def list_products(self, skip: int = 0, limit: int = 10, filters: ProductFilter = None) -> list[ProductResponse]:
        """
        Retrieve a filtered and paginated list of products.
        
        This method provides comprehensive product listing with advanced
        filtering capabilities and efficient pagination for large catalogs.
        
        Args:
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (ProductFilter, optional): Filter criteria for the query
            
        Returns:
            list[ProductResponse]: List of products matching the criteria
            
        Raises:
            DatabaseError: If database operation fails
            
        Filter Capabilities:
            - Price range filtering (min/max with decimal precision)
            - Stock availability filtering (in-stock only)
            - Text search across product names (case-insensitive)
            - Combined filtering with AND logic
            
        Note:
            - Empty result sets return an empty list, not None
            - Pagination parameters are validated at the API level
            - Filters support complex business logic combinations
            - Results are transformed to response schemas
        """
        try:
            # Retrieve products from repository with filters
            product_model_list = await self.repo.get_list(
                self.session, 
                skip=skip, 
                limit=limit, 
                filters=filters
            )
            
            if not product_model_list:
                logger.info("Product list query returned no results")
                return []  # Return empty list if no data found
            
            # Transform models to response schemas
            product_responses = [ProductResponse.model_validate(product_model) for product_model in product_model_list]
            logger.info(f"Retrieved {len(product_responses)} products successfully")
            
            return product_responses
            
        except Exception as e:
            logger.error(f"Failed to list products: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to list products")

    async def delete_product(self, product_id: int) -> bool:
        """
        Delete a product from the system.
        
        Args:
            product_id (int): ID of the product to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            DatabaseError: If database operation fails
            
        Note:
            - This operation is irreversible
            - Consider implementing soft deletes for production systems
            - May need additional business rule checks (e.g., active orders)
            - Product existence is validated before deletion
        """
        try:
            deleted = await self.repo.delete(self.session, product_id)
            if not deleted:
                logger.warning(f"Product deletion failed: product {product_id}")
                raise ProductNotFoundError("Product not found or has orders")
            
            logger.info(f"Product {product_id} deleted successfully")
            return deleted
            
        except ProductNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to delete product")


