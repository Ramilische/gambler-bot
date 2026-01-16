from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.basiclogging import log_message

router = Router()
start_message = """
Привет, я телеграм бот, посвященный азартным играм

Здесь можно узнать об этих играх и попробовать поиграть на виртуальной валюте без риска. Валюта пока не реализована

/roulette - рулетка
/dice - кости
"""

@router.message(Command(commands=['start']))
async def start(message: Message):
    log_message(message)
    
    await message.answer(start_message)
