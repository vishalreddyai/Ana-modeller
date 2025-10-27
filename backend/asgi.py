"""
ASGI config for Ana Modeller project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""
import os
from app.main import app

# For Uvicorn to find the application
application = app
