from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select,func
from config import get_db
from models import Review, Product,User,VendorApplication,ReviewReply
from schemas.review_schema import ReviewCreate,ReviewStatusUpdate,ReviewReplyHandler
from utils import get_current_user
from sqlalchemy.orm import selectinload
from services.product_services import get_product_by_id
from services.review_services import create_review_service,get_vendor_rating_service
from uuid import UUID


review_router= APIRouter(tags= ["Reviews and Ratings"])

@review_router.post("/{product_id}")
async def create_review(
    payload:ReviewCreate, 
    db: AsyncSession=Depends(get_db), 
    current_user=Depends(get_current_user)
    ):
    try:
        review= await create_review_service(db,payload,current_user.get("user_id"))

        return{
            "success": True,
            "status_code": 200,
            "data": review,
            "message" : "Review submitted successfully"
        }
    
    except HTTPException as e:
        print("e:",e)
        raise HTTPException (
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong"
        )
    except Exception as f:
        print("create_review:general:",f)
        raise HTTPException(
            status_code= 500,
            detail= "Internal server error"
        )


@review_router.get("/vendor-ratings/{vendor_id}")
async def get_vendor_rating(vendor_id: UUID, db: AsyncSession=Depends(get_db)):
    try:
        
        user,rating,total_reviews= await get_vendor_rating_service(db,vendor_id)

        return {
            "success": True,
            "status_code": 200,
            "message": "Vendor rating retrieved successfully",
            "data": {
                "vendor" : user,
                "rating": rating,
                "total_reviews": total_reviews
            }
        }

    except HTTPException as e:
        print ("Exception:",e)
        raise HTTPException(
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong while retrieving vendor ratings"
        )
    except Exception as h:
        print("get_vendor_rating general:", h)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )


@review_router.patch("/hide-review/{review_id}")
async def hide_review(
    review_id: UUID,
    payload: ReviewStatusUpdate,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
    ):
    try:
        query= select(Review).where(Review.id==review_id)
        review= (await db.execute(query)).scalar_one_or_none()
        if not review:
            raise HTTPException(
                status_code= 404,
                detail= "Review not found"
            )
        
        review.status = "archived" if payload.status == "archive" else "published"
    
        await db.commit()
        await db.refresh(review)
        return{
            "success": True,
            "status_code": 200,
            "message": f"Review {payload.status} successful",
            "data": {
                "id": review.id,
                "status": review.status
            }
        }
    except HTTPException as e:
        print("hide_review_Http_error:",e)
        raise HTTPException(
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong"
        )
    except Exception as f:
        print("Hide_review_general_error:",f)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )


@review_router.get("/product-reviews/{product_id}")
async def get_product_reviews(product_id:UUID, db:AsyncSession=Depends(get_db)):
    try:
        query= select(Product).where(Product.id == product_id)
        product= (await db.execute(query)).scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        query= select(Review).where(Review.product_id == product_id)
        reviews= (await db.execute(query)).scalars().all()

        return {
            "success": True,
            "status_code": 200,
            "message": "Product reviews retrieved successfully",
            "data": {
                "reviews": reviews
            }
        }
    except HTTPException as e:
        print("get_product_reviews_HTTP_error:",e)
        raise HTTPException(
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong"
        )
    except Exception as f:
        print("get_product_reviews_general_error:",f)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )
        

@review_router.post("/review-replies/{review_id}")
async def send_vendor_reply(
    payload: ReviewReplyHandler,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
  ):
    try:
        query= (select(Review).
        options(selectinload(Review.product)).
        where(Review.id==payload.review_id)
        )
        review= (await db.execute(query)).scalar_one_or_none()
        print("here",review.id)
        if not review:
            raise HTTPException(
                status_code= 404,
                detail= "Review not found"
            )
        select_exists_query = select(ReviewReply).where(ReviewReply.review_id==payload.review_id)
        reply_exists= (await db.execute(select_exists_query)).scalars().all()
        if reply_exists:
            raise HTTPException(
                status_code= 400,
                detail= "You have already replied to this review"
            )
        query= (select(VendorApplication)
        .where(VendorApplication.user_id==current_user["user_id"],
        VendorApplication.status=="approved"))
        vendor= (await db.execute(query)).scalar_one_or_none()
        print("here1")
        if not vendor:
            raise HTTPException(
                status_code=403,
                detail= "You are not authorized to reply to this review"
            )

        if vendor.user_id != review.product.user_id:
            raise HTTPException(
                status_code=403,
                detail= "You are not authorized to reply to this review"
            ) 
        
        reply= ReviewReply(
            **payload.model_dump(exclude_unset=True),
            vendor_id=current_user.get("user_id")
        )
        db.add(reply)
        await db.commit()
        print("here2")
        await db.refresh(reply)
        print("here3")
        return {
            "success": True,
            "status_code": 200,
            "message": "Reply sent successfully",
            "data": {
                # "vendor": vendor.user_id,
                "review": review,
                "reply": reply
            }
        }
    except HTTPException as e:
        print("send_vendor_reply_HTTP_error:",e)
        raise HTTPException(
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong"
        )
    except Exception as f:
        print("send_vendor_reply_general_error:",f)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )



    
