from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String, DateTime,UUID
from datetime import datetime
import uuid
from config import Base


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
   

class UserOTP(Base):
    __tablename__="user_otps"

    id :Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    otp : Mapped[str] = mapped_column(String(6),nullable=False,unique=True)
    expires_at: Mapped[datetime]  = mapped_column(DateTime,nullable=False)
    user_id :Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True),nullable=False)





# try:
        
#     file = open("path")

#     file.write("put somthing")
# finally:
#     file.close()

# with open("path") as file:
#     file.write(" cdjjdh")