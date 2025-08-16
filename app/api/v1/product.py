"""
Product API Controller Module

This module defines the REST API endpoints for product management operations.
It handles HTTP requests, input validation, error handling, and response
formatting for all product-related operations.

The controller layer is responsible for:
- HTTP request/response handling
- Input validation and sanitization
- Error handling and HTTP status codes
- Response formatting and serialization
- API documentation through OpenAPI schemas

API Endpoints:
- GET /products/{product_id} - Retrieve product by ID
- GET /products/ - List products with filtering and pagination
- POST /products/ - Create new product
- PUT /products/{product_id} - Update existing product
- DELETE /products/{product_id} - Delete product
"""

from fastapi import APIRouter, HTTPException
from app.core.dependencies import ProductServiceDep
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.exceptions import ProductNotFoundError, DatabaseError

# Create router instance for product endpoints
# All routes in this module will be prefixed with /products
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(service: ProductServiceDep, product_id: int):
    """
    Retrieve a product by its unique identifier.
    Args:
        service (ProductServiceDep): Injected product service dependency
        product_id (int): Unique identifier of the product to retrieve   
    Returns:
        ProductResponse: Complete product data
    """
    try:
        db_product = await service.get_product(product_id)
        return db_product
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve product at this time")


@router.get("/", response_model=list[ProductResponse])
async def list_products(service: ProductServiceDep, skip: int = 0, limit: int = 10):
    """
    Retrieve a paginated list of products.
    Args:
        service (ProductServiceDep): Injected product service dependency
        skip (int): Number of records to skip for pagination (default: 0)
        limit (int): Maximum number of records to return (default: 10, max: 100)  
    Returns:
        list[ProductResponse]: List of products with pagination
    """
    try:
        return await service.list_products(skip=skip, limit=limit)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve products at this time")


@router.post("/", response_model=ProductResponse)
async def create_product(service: ProductServiceDep, product: ProductCreate):
    """
    Create a new product in the system.
    Args:
        service (ProductServiceDep): Injected product service dependency
        product (ProductCreate): Product creation data from request body  
    Returns:
        ProductResponse: Created product data with generated ID
    """
    try:
        return await service.create_product(product)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to create product at this time")


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(service: ProductServiceDep, product_id: int, product: ProductUpdate):
    """
    Update an existing product in the system.
    Args:
        service (ProductServiceDep): Injected product service dependency
        product_id (int): Unique identifier of the product to update
        product (ProductUpdate): Product update data from request body  
    Returns:
        ProductResponse: Updated product data
    """
    try:
        return await service.update_product(product_id, product)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to update product at this time")


@router.delete("/{product_id}")
async def delete_product(service: ProductServiceDep, product_id: int):
    """
    Delete a product from the system.
    Args:
        service (ProductServiceDep): Injected product service dependency
        product_id (int): Unique identifier of the product to delete   
    Returns:
        dict: Success message confirming deletion
    """
    try:
        await service.delete_product(product_id)
        return {"message": "Product deleted successfully"}
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to delete product at this time")