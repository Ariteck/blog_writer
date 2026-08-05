import sys
import os
import uvicorn

# Add current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",   # MUST BE 0.0.0.0 inside Docker
        port=8000,
        reload=True,
        app_dir="."      # Tells reload worker to look in current folder
    )