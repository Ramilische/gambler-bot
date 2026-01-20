from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.basiclogging import log_message
from utils.fun import get_random_loss_message
from db.requests import UserRepository

router = Router()
dice_success_message = 'Вы выиграли!'
roulette_values = { # от 1 до 64 
    64: 50, # 64 - три семерки
    43: 40, # 43 - три лимона
    22: 30, # 22 - три винограда
    1: 20, # 1 - три BAR
    2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1, 10: -1, 11: -1, 12: -1, 13: -1, 14: -1, 15: -1, 16: -1,
    17: -1, 18: -1, 19: -1, 20: -1, 21: -1, 23: -1, 24: -1, 25: -1, 26: -1, 27: -1, 28: -1, 29: -1, 30: -1, 31: -1, 32: -1,
    33: -1, 34: -1, 35: -1, 36: -1, 37: -1, 38: -1, 39: -1, 40: -1, 41: -1, 42: -1, 44: -1, 45: -1, 46: -1, 47: -1, 48: -1,
    49: -1, 50: -1, 51: -1, 52: -1, 53: -1, 54: -1, 55: -1, 56: -1, 57: -1, 58: -1, 59: -1, 60: -1, 61: -1, 62: -1, 63: -1,
}


class DiceStates(StatesGroup):
    ask = State()

class RouletteStates(StatesGroup):
    confirm = State()


@router.message(Command(commands=['roulette']))
async def roulette(message: Message, state: FSMContext):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    await state.clear()
    await state.set_state(RouletteStates.confirm)
    await message.answer(text='Коэффициенты:\nТри семерки - х 50\nТри лимона - х 40\nТри винограда - х 30\nТри BAR - х 20\n\nНапишите размер ставки')

@router.message(RouletteStates.confirm)
async def check_roulette(message: Message, state: FSMContext):
    log_message(message)
    user = await UserRepository.get_user(tg_id=message.from_user.id) # type: ignore
    balance = user.balance if user else 0
    bet = 0
    
    if not message.text or not message.text.isdigit():
        return
    if message.text and message.text.isdigit():
        bet = int(message.text)
    
    if bet > balance:
        await message.answer(f'{bet} фишек - слишком большая ставка. Ваш баланс равен {balance}')

    result = await message.answer_dice(emoji='🎰')
    if result.dice:
        val = result.dice.value
        success = roulette_values[val] > 0
        if success:
            await message.answer(f'Поздравляю! Вы выиграли {bet * roulette_values[val]} фишек')
        else:
            await message.answer(get_random_loss_message())
        await UserRepository.add_money(message.from_user.id, bet * roulette_values[val]) # type: ignore
        await message.answer('Повторим? /roulette')
    await state.clear()


@router.message(Command(commands=['dice']))
async def dice(message: Message, state: FSMContext):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    await state.clear()
    await state.set_state(DiceStates.ask)
    await message.answer('Кидают 2 кости, четное число выпадет на костях или нечетное?\n\nчет - четное\nнечет - нечетное')


@router.message(DiceStates.ask)
async def check_dice(message: Message, state: FSMContext):
    log_message(message)
    
    if message.text and message.text.lower().startswith(('нечет', 'нечёт', 'чет', 'чёт')):
        is_odd = message.text.startswith(('нечет', 'нечёт'))
        result1 = await message.answer_dice()
        result2 = await message.answer_dice()
        if result1.dice and result2.dice:
            value1 = result1.dice.value
            value2 = result2.dice.value
            success = any([is_odd and (value1 + value2) % 2, not is_odd and not (value1 + value2) % 2])
            
            if success:
                await message.answer(dice_success_message)
            else:
                await message.answer(get_random_loss_message())
            await message.answer('Повторим? /dice')
    else:
        await message.answer('Что-то пошло не так')

    await state.clear()
