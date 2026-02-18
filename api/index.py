"""
Vercel serverless function entry point
Imports FastAPI app from main.py
"""

import sys
import os

# Add parent directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app

# Vercel expects a handler that works with ASGI
from mangum import Adapter

handler = Adapter(app)
