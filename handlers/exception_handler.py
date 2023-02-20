import os
from aiogram import types
from loader import bot


"""
Файл exception_handler.py - при возникновении ошибки в меню управления (удаление или получение информации)
присылает пользователям уведомление об ошибке.
"""


admin_url = os.getenv("ADMIN_NAME")


async def exception_hand(tg_id: int) -> None:
    start_buttons = ['Список площадок', "Список валют", 'Настройки']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(*start_buttons)
    await bot.send_message(tg_id, "Возникла ошибка:(\n"
                                  f"Напишите администратору {admin_url}",
                           reply_markup=keyboard)
