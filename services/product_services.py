from fastapi import HTTPException
from schemas.product_schema import ProductCreate
from sqlalchemy import select,func,or_,case
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models import Product,VendorApplication
from math import ceil


async def get_product_by_id(db:AsyncSession,product_id:UUID):
    product_query = select(Product).where(Product.id == product_id)
    product = (await db.execute(product_query)).scalar_one_or_none()
    return product



async def create_product_service(db:AsyncSession,body:ProductCreate,current_user_id:UUID):
    store_query = select(VendorApplication).where(VendorApplication.id == body.store_id)
    store = (await db.execute(store_query)).scalar_one_or_none()
    if not store:
        raise HTTPException(
            status_code=404,
            detail="Store not found",
        )
    if store.status != "approved":
        raise HTTPException(
            status_code=403,
            detail="Store is not approved",
        )
    payload= body.model_dump()
    new_product= Product(
        **payload,
        user_id=current_user_id
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

async def get_all_products_service(
    db:AsyncSession,
    page:int,
    pageSize:int,
    category:str,
    min_price:float,
    max_price:float,
    vendor:UUID,
    in_stock:bool,
    sort_by:str,
    search:str
    ):
    query= select(Product)
        
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code= 422,
                detail= "Min price cannot be greater than max price"
            )
    
    if search:
        search_text= search.strip().lower()
        pattern= f"%{search_text}%"

        query= query.where(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.store.has(VendorApplication.store_name.ilike(pattern)),
            )
        )
        relevance= case(
            (func.lower(Product.name)== search_text, 5),
            (Product.name.ilike(f"{search_text}%"), 4),
            (Product.name.ilike(pattern), 3),
            (Product.description.ilike(pattern), 2),
            (Product.store.has(VendorApplication.store_name.ilike(pattern)), 1),
            else_=0,
        )
    query= query.order_by(None)

    if sort_by in (None, "newest"):
        query= query.order_by(Product.created_at.desc())
    elif sort_by == "price_ascending":
        query= query.order_by(Product.price.asc())
    elif sort_by == "price_descending":
        print(sort_by)
        query= query.order_by(Product.price.desc())
    elif sort_by is None and search:
        query= query.order_by(relevance.desc())
    else:
        raise HTTPException(
            status_code= 422,
            detail= "Invalid sort by option",
        )
    print(category)
    if category is not None:
        print(category)
        query= query.where(Product.category==category)
    if min_price is not None:
        query= query.where(Product.price>=min_price)
    if max_price is not None:
        query= query.where(Product.price<=max_price)
    if vendor is not None:
        query= query.where(Product.user_id==vendor)
    if in_stock is True:
        query= query.where(Product.stock>0)
    elif in_stock is False:
        query= query.where(Product.stock==0)

    skip = (page - 1) * pageSize
    product_count = (await db.execute(select(func.count(Product.id)))).scalar()
    print(product_count)
    no_of_pages =  ceil(product_count/pageSize)
    print(no_of_pages)
    query= (query
            .options(selectinload(Product.store),selectinload(Product.user))
            .limit(pageSize)
            .offset(skip)
            # .where(Product.status=="published")
            )
            
    products = (await db.execute(query)).scalars().all()
    return products,no_of_pages,product_count