from fastapi import Request, Depends
from fastapi.responses import (
    Response,
    PlainTextResponse,
    HTMLResponse,
    RedirectResponse,
    JSONResponse
)
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_302_FOUND

import httpx
import base64

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from loguru import logger

from utils.db_model import BotStatus, User, Field, UserFieldValue
from utils.custom_types import (
    BotStatusEnum,
    FieldStatusEnum
)

from ui.setup import app, prefix_router, provider
from ui.helpers import verify_token, template

app.mount(f"{provider.config.path_prefix}/assets", StaticFiles(directory=f"{provider.config.box_bot_home}/src/ui/assets"), name="assets")

@prefix_router.get("/", tags=['status'])
async def root() -> RedirectResponse:
    """
    Перенаправляет на статус бота
    """
    return RedirectResponse(url=f"{provider.config.path_prefix}/status", status_code=HTTP_302_FOUND)

@prefix_router.get("/status", tags=["status"])
async def status(request: Request) -> HTMLResponse:
    """
    Показывает текущий статус работы бота
    """
    bot_status = await provider.bot_status

    return template(
        request=request, template_name="status.j2.html",
        additional_context = {
            'title':         provider.config.i18n.bot_status,
            'BotStatusEnum': BotStatusEnum,
            'bot_status':    bot_status
        }
    )

@prefix_router.post("/bot", tags=["bot"], dependencies=[Depends(verify_token)])
async def set_bot_status(action: str) -> JSONResponse:
    """
    Устанавливает статус работы бота
    """
    logger.success("Start set BotStatus...")
    async with provider.db_session() as session:
        if action == 'turn_off':
            await session.execute(update(BotStatus).values(bot_status = BotStatusEnum.OFF))
        elif action == 'turn_on':
            await session.execute(update(BotStatus).values(bot_status = BotStatusEnum.ON))
        elif action == 'restart':
            await session.execute(update(BotStatus).values(bot_status = BotStatusEnum.RESTART))
        elif action == 'activate_registration':
            await session.execute(update(BotStatus).values(is_registration_open = True))
        elif action == 'deactivate_registration':
            await session.execute(update(BotStatus).values(is_registration_open = False))

        try:
            await session.commit()
            logger.success("Set BotStatus table...")
            return JSONResponse({'error': False})
        except IntegrityError as err:
            logger.error(err)
            await session.rollback()
            logger.error("Did not set BotStatus table...")
            return JSONResponse({'error': True}, status_code=500)

@prefix_router.get("/users", tags=["users"])
async def settings(request: Request) -> HTMLResponse:
    """
    Показывает пользователей
    """

    async with provider.db_session() as session:
        fields_selected = await session.execute(
            select(Field)
            .where(Field.status == FieldStatusEnum.MAIN)
            .order_by(Field.id.asc())
        )
        fields = list(fields_selected.scalars())

        users_selected = await session.execute(
            select(User)
            .order_by(User.id.asc())
        )
        users = users_selected.scalars()

        users_field_values = [
            {
                'id': user.id,
                'chat_id': user.chat_id,
                'username': user.username
            } | {
                f"field-{field_value.field_id}": {
                    'value': field_value.value,
                    'document_bucket': field_value.field.document_bucket
                }
                for field_value in user.fields_values
            }
            for user in users
        ]

        return template(
            request=request, template_name="users.j2.html",
            additional_context = {
                'title': provider.config.i18n.users,
                'fields': fields,
                'users': users_field_values
            }
        )

@prefix_router.get("/minio/{bucket}/{filename}", tags=["minio"], dependencies=[Depends(verify_token)])
async def settings(bucket: str, filename: str) -> Response:
    """
    Прокси к minio
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:9000/{bucket}/{filename}")
    return Response(content=response.content, headers=response.headers, status_code=response.status_code)

@prefix_router.get("/minio/base64/{bucket}/{filename}", tags=["minio-base64"], dependencies=[Depends(verify_token)])
async def settings(bucket: str, filename: str) -> Response:
    """
    Прокси к minio
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:9000/{bucket}/{filename}")
    return JSONResponse(content = {
        'image': base64.b64encode(response.content).decode(),
        'mime':  response.headers['content-type']
    })

@prefix_router.get("/settings", tags=["settings"])
async def settings(request: Request) -> HTMLResponse:
    """
    Показывает настройки бота
    """
    curr_settings = await provider.settings

    settings_with_description = [
        {
            'key': key,
            'description': default_dict['description'],
            'value': getattr(curr_settings, key)
        }
        for key,default_dict in provider.config.defaults.model_dump().items()
    ]

    return template(
        request=request, template_name="settings.j2.html",
        additional_context = {
            'title':    provider.config.i18n.settings,
            'settings': settings_with_description
        }
    )

@prefix_router.get(f"/healz", tags=["healz"])
async def healz() -> PlainTextResponse:
    """
    Возвращает состояние сервера
    """
    return PlainTextResponse("OK")

app.include_router(prefix_router)