from fastapi import FastAPI
from routes import auth_routes,vendor_routes,product_routes,order_routes
from config import init_models
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_models()



app.include_router(auth_routes.auth_router,prefix="/auth")
app.include_router(vendor_routes.vendor_router,prefix="/vendors")
app.include_router(product_routes.product_router,prefix="/products")
app.include_router(order_routes.order_router,prefix="/orders")





