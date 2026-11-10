from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select,func
from models import Review,Product,User,Store
from services.product_services import get_product_by_id
from uuid import UUID


async def create_review_service(db,payload,current_user_id):
    product= await get_product_by_id(db,payload.product_id)
    print (product)
    if not product:
        raise HTTPException(
            status_code= 404,
            detail= "Product not found"
        )
    # print("product.user_id:",product.user_id)
    # print("current_user.get('user_id'):",current_user.get("user_id"))
    # print("are same:", product.user_id == current_user.get("user_id"))
    # print("user id type",type(str(product.user_id)))
    # print("token type",type(current_user.get("user_id")))
    if str(product.user_id) == current_user_id:
        raise HTTPException(
            status_code= 400,
            detail= "You cannot review your own product"
        )
    query= select(Review).where(
        Review.product_id == payload.product_id,
        Review.user_id == current_user_id
    )
    existing_review= (await db.execute(query)).scalar_one_or_none()
    if existing_review:
        raise HTTPException(
            status_code=409,
            detail= "You have already reviewed this product"
        )
        
    review= Review(
        **payload.model_dump(exclude_unset=True),
        user_id=current_user_id
    )
    print (review)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review

async def get_vendor_rating_service(db, vendor_id:UUID):
    query= (
            select(User)
            .where(User.user_id == vendor_id)
        )
    user= (await db.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=404,
            detail= "Vendor not found"
        )
    applications_query = (select(Store).
    where(Store.user_id==vendor_id,
    Store.status=='approved')
    )
    applications = (await db.execute(applications_query)).scalars().all()
    if not applications:
        raise HTTPException(
            status_code=404,
            detail= "Vendor not found"
        )
    
    query= (select (func.avg(Review.rating), func.count(Review.id))
    .where(Review.user_id == vendor_id))
    rating, total_reviews= (await db.execute(query)).one()

    return user,rating,total_reviews