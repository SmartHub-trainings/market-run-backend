from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker
from sqlalchemy import create_engine, Integer, Boolean, String, DateTime
from datetime import datetime

load_dotenv()

DATABASE_URL = os.get_env("DB_URL")

engine= create_engine(DATABASE_URL, connect_args= {"check_same_thread": False})
SessionLocal= sessionmaker(autocommit= False, autoflush= False, bind= engine)


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True)
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


Base.metadata.create_all(bind= engine)
