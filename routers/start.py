from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.basiclogging import log_message
from utils.messagebuilder import start_message
from db.requests import UserRepository

router = Router()


@router.message(Command(commands=['start']))
async def start(message: Message):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    await message.answer(start_message)
