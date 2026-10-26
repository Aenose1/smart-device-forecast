import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("app")


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code, self.code, self.message, self.details = status_code, code, message, details


def _resp(status: int, code: str, message: str, details=None):
    body = {"detail": message, "code": code}
    if details:
        body["details"] = details
    return JSONResponse(status_code=status, content=body)


def install_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app(_: Request, e: AppError):
        return _resp(e.status_code, e.code, e.message, e.details)

    @app.exception_handler(RequestValidationError)
    async def _val(_: Request, e: RequestValidationError):
        errs = [{"field": ".".join(str(p) for p in x["loc"] if p not in ("body", "query", "path")),
                 "message": x["msg"]} for x in e.errors()]
        return _resp(422, "validation_error", "The request was invalid.", {"errors": errs})

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, e: StarletteHTTPException):
        msg = {404: "Resource not found.", 405: "Method not allowed."}.get(e.status_code, str(e.detail))
        return _resp(e.status_code, "http_error", msg)

    @app.exception_handler(SQLAlchemyError)
    async def _db(request: Request, e: SQLAlchemyError):
        log.exception("Database error on %s", request.url.path)
        return _resp(503, "database_error", "The database is temporarily unavailable. Please try again shortly.")

    @app.exception_handler(Exception)
    async def _any(request: Request, e: Exception):
        log.exception("Unhandled error on %s", request.url.path)
        return _resp(500, "internal_error", "Something went wrong on our side. Please try again later.")
