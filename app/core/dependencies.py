from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.product import ProductService


# Asynchronous database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Product service dep
def get_product_service(session: SessionDep):
    return ProductService(session)


# Product service dep annotation
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]