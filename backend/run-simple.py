#!/usr/bin/env python3
"""Simple startup script for SpecSharp backend without heavy dependencies"""

import uvicorn
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Temporarily disable imports that require external dependencies
os.environ['SKIP_HEAVY_IMPORTS'] = '1'

if __name__ == "__main__":
    print("Starting SpecSharp Backend on http://localhost:8001")
    print("API Documentation: http://localhost:8001/docs")
    print("Press CTRL+C to stop")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )