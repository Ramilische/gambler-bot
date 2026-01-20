from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.basiclogging import log_message
from utils.messagebuilder import message_balance
from db.requests import UserRepository

router = Router()


class DebtStates(StatesGroup):
    pay = State()
    loan = State()


@router.message(Command(commands=['balance', 'money', 'account']))
async def balance(message: Message):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    info = await UserRepository.get_user(user.id) # type: ignore
    await message.answer(message_balance(user=info)) # type: ignore


@router.message(Command(commands=['getedebt', 'takedebt', 'debt', 'credit', 'zaim', 'loan', 'takeloan']))
async def takeloan(message: Message, state: FSMContext):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    info = await UserRepository.get_user(user.id) # type: ignore

    await state.clear()
    await state.set_state(DebtStates.loan)
    await message.answer(f'Баланс: {info.balance}\nВведите сумму, которую хотите взять в долг') # type: ignore


@router.message(DebtStates.loan)
async def add_debt(message: Message, state: FSMContext):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    amount = 0
    
    if not message.text or not message.text.isdigit():
        await state.clear()
        await message.answer('Это не похоже на число')
        return
    if message.text and message.text.isdigit():
        amount = int(message.text)

    await UserRepository.add_debt(user.id, amount) # type: ignore
    await UserRepository.add_money(user.id, amount) # type: ignore
    await message.answer(f'Успешно взят долг на сумму {amount} фишек')
    
    await state.clear()


@router.message(Command(commands=['paydebt', 'payback', 'pay', 'payloan']))
async def payback(message: Message, state: FSMContext):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    info = await UserRepository.get_user(user.id) # type: ignore

    await state.clear()
    await state.set_state(DebtStates.pay)
    await message.answer(f'Баланс: {info.balance}\nВведите сумму для оплаты долга') # type: ignore


@router.message(DebtStates.pay)
async def subtract_debt(message: Message, state: FSMContext):
    log_message(message)
    user = message.from_user
    if user and not await UserRepository.user_exists(user.id):
        await UserRepository.add_user(tg_id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)
    
    info = await UserRepository.get_user(user.id) # type: ignore
    amount = 0
    id = user.id # type: ignore
    debt = info.debt # type: ignore
    
    if not message.text or not message.text.isdigit():
        await state.clear()
        await message.answer('Это не похоже на число')
        return
    if message.text and message.text.isdigit():
        amount = int(message.text)
    if amount > info.balance: # type: ignore
        await message.answer('Недостаточно средств для оплаты долга в таком размере')
        await state.clear()
        return
    if amount > debt:
        amount = debt

    await UserRepository.add_debt(id, -amount)
    await UserRepository.add_money(id, -amount)
    await message.answer(f'Успешно погашен долг на сумму {amount} фишек')
    if amount == debt:
        await message.answer('Вы избавились от долгового рабства!')
    
    await state.clear()
