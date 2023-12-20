# from api.router import api_router
from fastapi import FastAPI, status, Request
from fastapi.responses import UJSONResponse
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlmodel import SQLModel


from app.config import settings
from app.api.router import api_router
from app.database import async_engine
from app.common.http_response_model import CommonResponse
from app.common.middleware import log_request_middleware
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.auth_middleware import AuthMiddleware

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

def get_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0",
        docs_url=f"{settings.API_PREFIX}/docs/",
        redoc_url=f"{settings.API_PREFIX}/redoc/",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        default_response_class=UJSONResponse,
    )

    # app.add_middleware(AuthMiddleware)

    @app.on_event("startup")
    async def on_startup():
        await init_db()

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )

    #  index route for health check
    @app.get("/api/v1/health-check", name="Health Check")
    async def root():
        await init_db()
        return {"message": "I am healthy all db tables are created"}

    app.include_router(router=api_router, prefix="/api/v1")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        error_message = exc.detail if exc.detail else "An error occurred."
        status_code = exc.status_code if exc.status_code else status.HTTP_500_INTERNAL_SERVER_ERROR
        response = CommonResponse(
            success=False,
            message=error_message,
            payload=[]
        )
        return JSONResponse(status_code=status_code , content=response.dict())
    

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        response = CommonResponse(
            success=False,
            message="Unprocessable Entity",
            payload=str(exc)
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response.dict())
    
    app.middleware("http")(log_request_middleware)
    # app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    # app.add_exception_handler(HTTPException, http_exception_handler)
    # app.add_exception_handler(Exception, unhandled_exception_handler)

    return app