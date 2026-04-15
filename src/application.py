import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src_external.exception.exception_handlers import setup_exception_handlers
from src_external.ExternalAuthors.router import router as author_router
from src_external.ExternalStudents.router import router as student_router
from src_external.ExternalUsers.router import router as user_router


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=True,
        allow_origin_regex=r"http://localhost:.*",
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("Запуск приложения")
    app.include_router(author_router)
    app.include_router(student_router)
    app.include_router(user_router)
    setup_exception_handlers(app)
    return app


