from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.basiclogging import log_message

router = Router()
dice_success_message = 'Вы выиграли!'
dice_failure_message = 'Вы проиграли!'
roulette_values = { # от 1 до 64 
    64: 50, # 64 - три семерки
    43: 40, # 43 - три лимона
    22: 30, # 22 - три винограда
    1: 20, # 1 - три BAR
}


class DiceStates(StatesGroup):
    ask = State()

class RouletteStates(StatesGroup):
    confirm = State()


@router.message(Command(commands=['roulette']))
async def roulette(message: Message, state: FSMContext):
    log_message(message)
    
    await state.clear()
    await state.set_state(RouletteStates.confirm)
    await message.answer(text='Коэффициенты:\nТри семерки - х 50\nТри лимона - х 40\nТри винограда - х 30\nТри BAR - х 20\n\nНапишите размер ставки')

@router.message(RouletteStates.confirm)
async def check_roulette(message: Message, state: FSMContext):
    log_message(message)
    
    bet = 0
    total = 0
    if not message.text or not message.text.isdigit():
        print(message.text)
        return
    if message.text and message.text.isdigit():
        bet = int(message.text)

    result = await message.answer_dice(emoji='🎰')
    if result.dice:
        val = result.dice.value
        if val in roulette_values.keys():
            total = bet * roulette_values[val]
            await message.answer(f'Вы выиграли {total} фишек')
        else:
            await message.answer('Не повезло')
    await state.clear()


@router.message(Command(commands=['dice']))
async def dice(message: Message, state: FSMContext):
    log_message(message)
    
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
                await message.answer(dice_failure_message)
    else:
        await message.answer('Что-то пошло не так')

    await state.clear()
