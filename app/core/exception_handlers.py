from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    # ─── 422 Validation Error ──────────────────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(e) for e in error["loc"]),
                "message": error["msg"],
            })
        logger.warning(f"Validation error on {request.url}: {errors}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "detail": errors
            }
        )

    # ─── 404 Not Found ─────────────────────────────────────────────────────────
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        logger.warning(f"404 Not Found: {request.url}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "detail": f"Route {request.url.path} does not exist"
            }
        )

    # ─── 401 Unauthorized ──────────────────────────────────────────────────────
    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "detail": exc.detail or "Authentication required"
            }
        )

    # ─── 403 Forbidden ─────────────────────────────────────────────────────────
    @app.exception_handler(403)
    async def forbidden_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=403,
            content={
                "error": "Forbidden",
                "detail": exc.detail or "You don't have permission to access this resource"
            }
        )

    # ─── SQLAlchemy Database Errors ────────────────────────────────────────────
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error on {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database Error",
                "detail": "An unexpected database error occurred"
            }
        )

    # ─── Generic 500 Internal Server Error ────────────────────────────────────
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error on {request.url}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred"
            }
        )