import uvicorn
from app.config import settings

def main() -> None:
    
    print(f"Starting server... {settings.HOST}:{settings.PORT}")
    """Entrypoint of the application."""
    uvicorn.run(
        "app.app:get_app",
        workers=settings.WORKERS_COUNT,
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.RELOAD,
        factory=True,
    )


if __name__ == "__main__":
    main()