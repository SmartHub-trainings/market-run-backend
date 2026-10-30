from sqlalchemy.sql.functions import user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from sqlalchemy import select
from config import get_db
from schemas.order_schema import CartItemCreate
from models import CartItem
from utils import get_current_user
from sqlalchemy.orm import selectinload

order_router = APIRouter(tags=["Orders"])


@order_router.post("/cart-items")
async def add_item_to_cart(payload:CartItemCreate,
                            db:AsyncSession=Depends(get_db),
                            current_user =Depends(get_current_user)):
    print(payload)
    user_id = current_user.get("user_id")

    cart_item = CartItem(
        product_id=payload.product_id,
        qty=payload.qty,
        user_id=user_id

    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return {"message":"Item added to cart",
                "success":True,"status_code":201,
                "data":cart_item}

@order_router.get("/cart-items")
async def get_cart_items_of_current_user(db:AsyncSession=Depends(get_db),
                            current_user =Depends(get_current_user)):
    query= select(CartItem).where(CartItem.user_id==current_user.get("user_id")).options(selectinload(CartItem.product))
    cart_items= (await db.execute(query)).scalars().all()

    return {"message":"Item added to cart",
                "success":True,"status_code":201,
                "data":cart_items}





