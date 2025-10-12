import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gram Backend API")

# CORS middleware - ALLOW NETLIFY FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://inquisitive-capybara-c74bdf.netlify.app",  # Your Netlify domain
        "https://68e95bfbebac9106478eb847--inquisitive-capybara-c74bdf.netlify.app",  # Your Netlify preview
        "https://*.netlify.app"  # All Netlify subdomains
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Gram Backend API - Active", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Include all your routers
try:
    from app.routers import (analytics, auth, crop, farmer, market,
                             notifications, transactions, vendor)
    
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
    app.include_router(farmer.router, prefix="/farmers", tags=["farmers"])
    app.include_router(market.router, prefix="/market", tags=["market"])
    app.include_router(crop.router, prefix="/crops", tags=["crops"])
    app.include_router(vendor.router, prefix="/vendors", tags=["vendors"])
    app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
    app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
    
    print("✅ All routers loaded successfully!")
except Exception as e:
    print(f"❌ Router loading error: {e}")

# Auto-create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        from app import models
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Database error: {e}")