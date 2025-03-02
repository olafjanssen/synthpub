"""
Script to run the FastAPI application.
"""
import os
import uvicorn

def main():
    """Run the FastAPI application."""
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main() 