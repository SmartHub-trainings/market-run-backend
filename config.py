from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import secret

engine= create_engine(DATABASE_URL, connect_args= {"check_same_thread": False})
SessionLocal= sessionmaker(autocommit= False, autoflush= False, bind= engine)
