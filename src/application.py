import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.models.exception.exception_handlers import setup_exception_handlers
from src.models.authors.router import router as author_router



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
    setup_exception_handlers(app)
    return app


