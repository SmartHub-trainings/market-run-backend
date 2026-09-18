from sqlalchemy import Nullable
from email.policy import default
from sqlalchemy import Integer
from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, String, DateTime,UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import  create_async_engine,async_sessionmaker
import uuid

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
# type hint

engine= create_async_engine(DATABASE_URL)
SessionLocal= async_sessionmaker(autocommit= False, autoflush= False, bind= engine)


class Base(DeclarativeBase):
    pass

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
     async with SessionLocal() as db:
        yield db



class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique= True, nullable= False)
    first_name: Mapped[str] = mapped_column(String, nullable= False)
    last_name: Mapped[str] = mapped_column(String, nullable= False)
    password: Mapped[str] = mapped_column(String, nullable= False)
    phone: Mapped[str] = mapped_column(String, nullable= False)
    role: Mapped[str] = mapped_column(String, default= "user")
    email_is_verified: Mapped[bool] = mapped_column(Boolean, default= False)
    phone_is_verified: Mapped[bool] = mapped_column(Boolean, default= False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default= datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default= datetime.now)

class UserOTP(Base):
    __tablename__="user_otps"

    id :Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    otp : Mapped[str] = mapped_column(String(6),nullable=False,unique=True)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.now)
    expires_at: Mapped[datetime]  = mapped_column(DateTime,nullable=False)
    user_id :Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True),nullable=False)





# try:
        
#     file = open("path")

#     file.write("put somthing")
# finally:
#     file.close()

# with open("path") as file:
#     file.write(" cdjjdh")