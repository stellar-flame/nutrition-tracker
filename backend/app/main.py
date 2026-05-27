import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.database.database import get_engine, get_session
from .api.routers import nutrition, app_health, internal, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()
logger = logging.getLogger(__name__)


origins = [
    "https://www.nutritionapptracker.com",
    "http://localhost:5173",
    # add https://your-cloudfront-domain.com later if you use CloudFront
]

@app.middleware("http")
async def catch_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content={"message": "An internal error occurred"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code >= 500:
        logger.error("HTTP error on %s %s: %s", request.method, request.url.path, exc.detail)
    else:
        logger.info("HTTP error on %s %s: %s", request.method, request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(nutrition.router)
app.include_router(app_health.router)   
app.include_router(internal.router)
app.include_router(users.router)