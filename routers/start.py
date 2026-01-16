from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()
start_message = """
Привет, я телеграм бот, посвященный азартным играм

Здесь можно узнать об этих играх и попробовать поиграть на виртуальной валюте без риска"""

@router.message(Command(commands=['start']))
async def start(message: Message):
    await message.answer(start_message)
