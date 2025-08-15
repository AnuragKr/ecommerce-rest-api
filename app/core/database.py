from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel
import asyncio

from app.config import db_settings

# Base class for all models
Base = SQLModel

# Create a database engine to connect with database
engine = create_async_engine(
    # database type/dialect and file name
    url=db_settings.get_database_url,
    # Log sql queries
    echo=True,
)


async def get_session():
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


async def check_db():
    async for session in get_session():
        try:
            await session.execute(text("SELECT 1"))
            print("Database connected")
        except Exception as e:
            print(db_settings.get_database_url)
            print("Database NOT connected:", e)


async def create_tables():
    """Create all tables if they don't exist."""
    try:
        async with engine.begin() as conn:
            # Check if sales schema exists, create if not
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS sales"))
            print("Schema 'sales' created or already exists")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("All tables created successfully")
            
    except Exception as e:
        print(f"Error creating tables: {e}")


async def check_tables():
    """Check if required tables exist."""
    async for session in get_session():
        try:
            # Check if products table exists in sales schema
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'sales' 
                    AND table_name = 'products'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("Table 'sales.products' exists")
                
                # Check table structure
                result = await session.execute(text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_schema = 'sales' 
                    AND table_name = 'products'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print("Table structure:")
                for col in columns:
                    print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
            else:
                print("Table 'sales.products' does not exist")
                
        except Exception as e:
            print(f"Error checking tables: {e}")


# Uncomment to run database checks
# asyncio.run(check_db())
# asyncio.run(create_tables())
# asyncio.run(check_tables())