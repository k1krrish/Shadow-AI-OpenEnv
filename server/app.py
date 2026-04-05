import uvicorn
from src.main import app

def main():
    """Entry point for the openenv multi-mode deployment server."""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
