from fastapi import FastAPI, APIRouter
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager

from ui.ui_provider import UIProvider

description = """
UI сервис для управления ботами в коробках
"""

tags_metadata = [
    {
        "name": "status",
        "description": "Статус работы бота",
    },
    {
        "name": "bot",
        "description": "Управление состоянием бота",
    },
    {
        "name": "settings",
        "description": "Получить настройки приложения",
    },
    {
        "name": "healz",
        "description": "Отвечает если приложение живо",
    }
]

provider = UIProvider()

@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Асинхронная инциализация провайдера при старте приложения
    """
    await provider.async_init()
    yield

app = FastAPI(
    title        = "Box Bot Admin UI",
    description  = description,
    openapi_tags = tags_metadata,
    version      = "0.0.1",
    redoc_url    = f"{provider.config.path_prefix}/redoc",
    docs_url     = f"{provider.config.path_prefix}/docs",
    openapi_url  = f"{provider.config.path_prefix}/openapi.json",
    lifespan     = lifespan
)

prefix_router = APIRouter(prefix = provider.config.path_prefix)

templates = Jinja2Templates(directory = f"{provider.config.box_bot_home}/src/ui/templates")