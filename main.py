from fastapi import FastAPI
from routes import auth_routes
from config import init_models


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_models()



app.include_router(auth_routes.auth_router,prefix="/auth")



