from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
import time
import logging
from scalar_fastapi import get_scalar_api_reference
from app.config import project_settings
from app.core.database import engine, Base
from app.api.v1.product import router as product_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """ Create FastAPI application with all configurations. """
    
    app = FastAPI(
        title=project_settings.PROJECT_NAME,
        description="Production-grade E-commerce API",
        version=project_settings.VERSION,
        openapi_url=f"{project_settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Include routers
    app.include_router(product_router)
    
    return app


# Create the application instance
app = create_application()

### Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )