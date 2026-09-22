from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import  create_async_engine,async_sessionmaker
from secret import DATABASE_URL
from passlib.context import CryptContext

engine= create_async_engine(DATABASE_URL)
SessionLocal= async_sessionmaker(autocommit= False, autoflush= False, bind= engine)

password_context= CryptContext(schemes=['bcrypt'], deprecated= "auto")

class Base(DeclarativeBase):
    pass

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
     async with SessionLocal() as db:
        yield db