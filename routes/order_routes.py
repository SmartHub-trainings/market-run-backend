from fastapi import HTTPException
from sqlalchemy.sql.functions import user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from sqlalchemy import select,delete
from config import get_db
from schemas.order_schema import CartItemCreate,OrderCreate
from models import CartItem,Order,OrderItem
from utils import get_current_user
from sqlalchemy.orm import selectinload
from services.product_services import get_product_by_id

order_router = APIRouter(tags=["Orders"])


@order_router.post("/cart-items")
async def add_item_to_cart(payload:CartItemCreate,
                            db:AsyncSession=Depends(get_db),
                            current_user =Depends(get_current_user)):
    print(payload)
    product = await get_product_by_id(db,payload.product_id)
    if product.stock<payload.qty:
        raise HTTPException(status_code=400,detail="Insuffiient stock quantity")
    

    user_id = current_user.get("user_id")
    cart_query = select(CartItem).where(CartItem.user_id==user_id,CartItem.product_id==payload.product_id)
    cart_item= (await db.execute(cart_query)).scalar_one_or_none()
    if cart_item:
        cart_item.qty=payload.qty
        db.add(cart_item)
        await db.commit()
        await db.refresh(cart_item)
    else:
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

@order_router.post("")
async def create_new_order_handler(payload:OrderCreate,
                                    db:AsyncSession=Depends(get_db),
                                    current_user =Depends(get_current_user)):

    try:

        items =payload.order_items
        PROCESSING_FEE_PCT=10
        sub_total = 0
        for item in items:
            product = await get_product_by_id(db,item.product_id)
            sub_total += product.price*item.qty
            # print("price",product.price)
        processing_fee = sub_total*PROCESSING_FEE_PCT/100
        total = processing_fee+sub_total
        order = Order(
            user_id =current_user.get("user_id"),
            total_amount = total,
            payment_status = "success"
        )
        
        db.add(order)
        await db.flush()
        # print("after staging order")

        # pre_order_items =[]
        for item in items:
            product= await get_product_by_id(db,item.product_id)
            order_item = OrderItem(
                product_id =product.id,
                order_id =order.id,
                unit_price =product.price,
                qty=item.qty
            )
            db.add(order_item)
            await db.flush()
            product.stock = product.stock-item.qty

            db.add(product)
            await db.flush()

        
        delete_query =delete(CartItem).where(CartItem.user_id==current_user.get("user_id"))
        await db.execute(delete_query)
        # print("before commit")
        await db.commit()
        return {"message":"order create successfully","success":True,"status_code":201,"data":order}

            # pre_order_items.append({"product_id":product.id,"qty":item.qty,"unit_price":product.price,"order_id":order.id}
    except Exception as e:
        print(e)
        print("rolling back!!")
        await db.rollback()

        raise HTTPException(status_code=500,detail="Something went wrong!")




