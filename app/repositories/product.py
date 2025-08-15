from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.product import Product
from app.schemas.product import ProductFilter

class ProductRepository:
    async def get_by_id(self, db: AsyncSession, product_id: int) -> Product:
        result = await db.execute(select(Product).where(Product.product_id == product_id))
        return result.scalar_one_or_none()

    async def get_list(
        self, db: AsyncSession, skip: int = 0, limit: int = 10, filters: ProductFilter = None
    ) -> list[Product]:
        query = select(Product)
        conditions = []
        if filters:
            if filters.price_min is not None:
                conditions.append(Product.price >= filters.price_min)
            if filters.price_max is not None:
                conditions.append(Product.price <= filters.price_max)
            if filters.in_stock_only:
                conditions.append(Product.stock_quantity > 0)
            if filters.search:
                conditions.append(Product.name.ilike(f"%{filters.search}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, create_data: dict) -> Product:
        db_obj = Product(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, product_id: int, update_data: dict) -> Product:
        db_obj = await self.get_by_id(db, product_id)  # make sure get_by_id is async
        if not db_obj:
            return None
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, product_id: int) -> bool:
        db_obj = await self.get_by_id(db, product_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True
