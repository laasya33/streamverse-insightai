import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import chat, analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="StreamVerse InsightAI API",
    description="Secure AI analytics assistant for StreamVerse Entertainment",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(analytics.router)

@app.on_event("startup")
async def startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("StreamVerse InsightAI started successfully")

@app.get("/")
async def root():
    return {"status": "ok", "service": "StreamVerse InsightAI API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
