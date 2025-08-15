from fastapi import APIRouter, HTTPException
from app.core.dependencies import ProductServiceDep
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.exceptions import ProductNotFoundError, DatabaseError

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(service: ProductServiceDep, product_id: int):
    try:
        db_product = await service.get_product(product_id)
        return db_product
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve product at this time")

@router.get("/", response_model=list[ProductResponse])
async def list_products(service: ProductServiceDep, skip: int = 0, limit: int = 10):
    try:
        return await service.list_products(skip=skip, limit=limit)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve products at this time")

@router.post("/", response_model=ProductResponse)
async def create_product(service: ProductServiceDep, product: ProductCreate):
    try:
        return await service.create_product(product)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to create product at this time")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(service: ProductServiceDep, product_id: int, product: ProductUpdate):
    try:
        return await service.update_product(product_id, product)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to update product at this time")

@router.delete("/{product_id}")
async def delete_product(service: ProductServiceDep, product_id: int):
    try:
        await service.delete_product(product_id)
        return {"message": "Product deleted successfully"}
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to delete product at this time")