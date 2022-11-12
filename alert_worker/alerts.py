import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from emoji import emojize
from aiogram.utils import markdown
from loader import bot
from db.crud import Database
from alert_worker import http_req
from alert_worker.handler_of_currency import counter_of_currencies
from alert_worker.template_fabric import content_creator
from handlers.exception_handler import exteption_heand
from logs.logger import logger


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
service_url = os.getenv("SERVICE_URL")


USER_CACHE = []


async def update_user_cache() -> None:
    """Обновление кэша при старте приложения и добавления нового пользователя"""
    global USER_CACHE
    USER_CACHE = await Database().notifications_state()


async def background_alerts() -> None:
    """Бесконечный цикл с запросами к биржам и отправке уведомлений"""
    await update_user_cache()
    global USER_CACHE
    try:
        while True:
            raw_data = await data_collector()
            data = counter_of_currencies(*raw_data)
            content: list = content_creator(data)
            if content != [] and USER_CACHE != []:
                for tg_id, state in USER_CACHE:
                    if state == "ACTIVATED":
                        await bot.send_message(chat_id=tg_id,
                                               text=emojize(markdown.text(*content), language='alias'),
                                               parse_mode='html')

    except Exception as ex:
        logger.exception(f"Exception on alerts loop {ex}")
        for tg_id, state in USER_CACHE:
            if state == "ACTIVATED":
                await exteption_heand(tg_id)


async def data_collector() -> list[dict]:
    """Сборщик данных с различных бирж"""
    all_data = []
    async with aiohttp.ClientSession(service_url) as session:
        list_of_requests = [
            http_req.binance_info(session),
            http_req.kucoin_info(session),
            http_req.huobi_info(session),
            http_req.okx_info(session)
        ]
        for task in list_of_requests:
            try:
                result = await asyncio.wait_for(task, timeout=3)
            except asyncio.TimeoutError:
                result = {"response": "TimeoutError"}
            all_data.append(result)

    return all_data


