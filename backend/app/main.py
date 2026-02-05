import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.database.database import get_engine, get_session
from .api.routers import nutrition, app_health, internal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()
logger = logging.getLogger(__name__)


origins = [
    "http://nutritionapptracker.com",
    "http://localhost:5173",
    # add https://your-cloudfront-domain.com later if you use CloudFront
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning("HTTP error on %s %s: %s", request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"message": f"An error occurred: {str(exc)}"},
    )


app.include_router(nutrition.router)
app.include_router(app_health.router)   
app.include_router(internal.router)