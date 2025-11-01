from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from rotoger import Rotoger

from api.user import router as user_router
from config import settings as global_settings
from exception_handlers.registry import register_exception_handlers
from redis_ import get_redis

logger = Rotoger().get_logger()


templates = Jinja2Templates(directory=Path(
    __file__).parent.parent / "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.redis = await get_redis()
    postgres_dsn = global_settings.postgres_url.unicode_string()
    try:
        app.postgres_pool = await asyncpg.create_pool(
            dsn=postgres_dsn,
            min_size=5,
            max_size=20,
        )
        await logger.ainfo(
            "Postgres pool created", idle_size=app.postgres_pool.get_idle_size()
        )
        yield
    except Exception as e:
        await logger.aerror("Error during app startup", error=repr(e))
        raise
    finally:
        await app.redis.close()
        await app.postgres_pool.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Stuff And Nonsense API",
        version="0.20.0",
        lifespan=lifespan
    )
    register_exception_handlers(app)

    @app.get("/index", response_class=HTMLResponse)
    def get_index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    app.include_router(user_router)

    return app


if __name__ == "__main__":
    app = create_app()
    import uvicorn
    uvicorn.run(app, port=8080, host="localhost")
