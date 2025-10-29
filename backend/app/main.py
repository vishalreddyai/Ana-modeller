"""
Main FastAPI application module.

This module creates and configures the FastAPI application instance.
"""

# Import FastAPI and other required modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Import routers
from app.routers import auth, stories, models

# Create FastAPI application instance
app = FastAPI(
    title="Ana Modeller API",
    version="1.0.0",
    description="API for Ana Modeller application",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(stories.router, prefix="/api/stories", tags=["User Stories"])
app.include_router(models.router, prefix="/api/models", tags=["Models"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "message": "Ana Modeller API is running"}


# Redirect the root path to the API docs for convenience
@app.get("/")
async def root_redirect():
    """Redirect the root URL to the API documentation."""
    return RedirectResponse(url="/api/docs")
