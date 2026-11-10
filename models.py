from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String, DateTime,UUID,Integer,Float,JSON,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from config import Base

# class Role()


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
    #role: Mapped[str] = mapped_column(String, default= "user")
    email_is_verified: Mapped[bool] = mapped_column(Boolean, default= False)
    phone_is_verified: Mapped[bool] = mapped_column(Boolean, default= False)
    stores: Mapped[list["Store"]] = relationship(back_populates="user")
    role: Mapped[str]=mapped_column(String(20),nullable=False,default="user")
   

class UserOTP(Base):
    __tablename__="user_otps"

    id :Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    otp : Mapped[str] = mapped_column(String(6),nullable=False,unique=True)
    expires_at: Mapped[datetime]  = mapped_column(DateTime,nullable=False)
    user_id :Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True),nullable=False)


"""
Vendors submit an application containing storefront name, category,
 description, bank account details, 
and a business-owner name. Applications enter a pending queue for admin review.
"""

class Store(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    store_name: Mapped[str] = mapped_column(String, nullable= False)
    category: Mapped[str] = mapped_column(String, nullable= False)
    description: Mapped[str] = mapped_column(String, nullable= False)
    bank_name: Mapped[str] = mapped_column(String, nullable= False)
    bank_account_number: Mapped[str] = mapped_column(String(10), nullable= False)
    bank_account_name: Mapped[str] = mapped_column(String, nullable= False)
    status: Mapped[str] = mapped_column(String, default= "pending")
    user_id : Mapped[uuid.UUID]= mapped_column(ForeignKey("users.user_id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="stores")



"""Approved vendors can create, edit, and delete their own products.
 A product carries name, description, 
price in NGN, category, up to five images, and inventory count."""

class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable= False)
    description: Mapped[str] = mapped_column(String, nullable= False)
    price: Mapped[float] = mapped_column(Float, nullable= False)
    category: Mapped[str] = mapped_column(String, nullable= False)
    images: Mapped[list] = mapped_column(JSON, nullable= False)
    stock: Mapped[int] = mapped_column(Integer, nullable= False)
    status: Mapped[str] = mapped_column(String, nullable= False,default='draft')
    user_id : Mapped[uuid.UUID]= mapped_column(ForeignKey("users.user_id"), nullable=False)
    user: Mapped["User"] = relationship()
    store_id :Mapped[uuid.UUID]= mapped_column(ForeignKey("stores.id"), nullable= False)
    store: Mapped["Store"] = relationship()

class CartItem(Base):
    __tablename__="cart_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 primary_key= True,
                                                 default=uuid.uuid4)
    user_id : Mapped[uuid.UUID]= mapped_column(ForeignKey("users.user_id"), nullable=False)
    user: Mapped["User"] = relationship()
    product_id : Mapped[uuid.UUID]= mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship()
    qty:Mapped[int]= mapped_column(Integer,nullable=False,default=1)


class Review(Base):
    __tablename__="reviews"

    id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True),
                                    primary_key=True,
                                    default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("users.user_id"), nullable=False)
    user: Mapped["User"]= relationship()
    product_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"]= relationship()
    status: Mapped[str]= mapped_column(String, nullable=False, default="published")
    rating: Mapped[int]= mapped_column(Integer, nullable=False)
    text: Mapped[str]= mapped_column(String(2000), nullable=True)
    #replies: Mapped[list["ReviewReply"]] = relationship()


class ReviewReply(Base):
    __tablename__ = "review_replies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                    primary_key=True,
                                    default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    vendor: Mapped["User"] = relationship()
    review_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reviews.id"), nullable=False)
    review: Mapped["Review"] = relationship()
    reply: Mapped[str] = mapped_column(String(2000), nullable=False) 

class Order(Base):
    __tablename__='orders'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                    primary_key=True,
                                    default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("users.user_id"), nullable=False)
    user: Mapped["User"]= relationship()
    total_amount :Mapped[float]= mapped_column(Float,nullable=False)
    status: Mapped[str] = mapped_column(String(20),nullable=False,default="pending")## delivered,canceled,'sent-out'
    payment_status: Mapped[str] = mapped_column(String(20),nullable=False,default="proccessing") # success,failed
    items:Mapped[list["OrderItem"]]=relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                    primary_key=True,
                                    default=uuid.uuid4)
    order_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["Order"]= relationship(back_populates="items")
    product_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"]= relationship()
    qty :Mapped[int] = mapped_column(Integer,nullable=False, default=1)
    unit_price :Mapped[float] = mapped_column(Float,nullable=False)



    




# try:
        
#     file = open("path")

#     file.write("put somthing")
# finally:
#     file.close()

# with open("path") as file:
#     file.write(" cdjjdh")