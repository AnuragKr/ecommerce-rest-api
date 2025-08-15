from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product import ProductRepository
from app.schemas.product import ProductResponse, ProductFilter, ProductCreate, ProductUpdate
from app.exceptions import ProductNotFoundError, DatabaseError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository()
        self.session = session

    async def create_product(self, product_in: ProductCreate) -> ProductResponse:
        try:
            # Set timestamps automatically
            create_data = product_in.model_dump()
            current_time = datetime.now()
            create_data['created_at'] = current_time
            create_data['updated_at'] = current_time
            
            product_model = await self.repo.create(self.session, create_data)
            return ProductResponse.model_validate(product_model)
        except Exception as e:
            logger.error(f"Failed to create product: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to create product")

    async def update_product(self, product_id: int, product_in: ProductUpdate) -> ProductResponse:
        try:
            # Set updated_at timestamp automatically
            update_data = product_in.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.now()
            
            product_model = await self.repo.update(self.session, product_id, update_data)
            if not product_model:
                logger.warning(f"Product {product_id} not found for update")
                raise ProductNotFoundError("Product not found")
            return ProductResponse.model_validate(product_model)
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to update product")

    async def get_product(self, product_id: int) -> ProductResponse:
        try:
            product_model = await self.repo.get_by_id(self.session, product_id)
            if not product_model:
                logger.warning(f"Product {product_id} not found")
                raise ProductNotFoundError("Product not found")
            return ProductResponse.model_validate(product_model)
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve product {product_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve product")

    async def list_products(self, skip: int = 0, limit: int = 10, filters: ProductFilter = None) -> list[ProductResponse]:
        try:
            product_model_list = await self.repo.get_list(self.session, skip=skip, limit=limit, filters=filters)
            if not product_model_list:
                return []  # Return empty list if no data found
            return [ProductResponse.model_validate(product_model) for product_model in product_model_list]
        except Exception as e:
            logger.error(f"Failed to list products: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to list products")

    async def delete_product(self, product_id: int) -> bool:
        try:
            deleted = await self.repo.delete(self.session, product_id)
            if not deleted:
                logger.warning(f"Product {product_id} not found for delete")
                raise ProductNotFoundError("Product not found")
            return deleted
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to delete product")


