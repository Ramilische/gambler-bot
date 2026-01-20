from sys import stdout

from sqlalchemy import select, update, delete, func
from pydantic import BaseModel, ConfigDict
from typing import List

from db.session import async_session
from db.models import User


class UserRepository:
    @classmethod
    async def user_exists(cls, tg_id: int) -> bool:
        """
        Проверка существования записи о пользователе в базе данных
                
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :return: Существует ли пользователь в базе
        :rtype: bool
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                return True
            return False
    
    @classmethod
    async def get_user(cls, tg_id: int) -> User | None:
        """
        Возвращает всю информацию о пользователе
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :return: Объект пользователя
        :rtype: User | None
        """
        async with async_session() as session:
            if not await cls.user_exists(tg_id=tg_id):
                return None
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            return user # type: ignore
    
    @classmethod
    async def add_user(cls, tg_id: int, first_name: str | None, last_name: str | None, username: str | None):
        """
        Проверяет, существует ли пользователь. Если нет - создает запись в БД. 
        Функция используется при /start и не только
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :param first_name: Имя пользователя
        :type first_name: str | None
        :param last_name: Фамилия пользователя
        :type last_name: str | None
        :param username: Ник пользователя
        :type username: str | None
        """
        async with async_session() as session:
            user_exists = await cls.user_exists(tg_id=tg_id)
            if user_exists:
                return 'User exists already'
            
            new_user = User(tg_id=tg_id, first_name=first_name, last_name=last_name, username=username)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user
    
    @classmethod
    async def change_balance(cls, tg_id: int, new_balance: int):
        """
        Метод для изменения баланса на новое значение
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :param new_balance: Новая сумма на балансе пользователя
        :type new_balance: int
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.balance = new_balance
            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def add_money(cls, tg_id: int, amount: int):
        """
        Метод для изменения баланса на какую-то сумму, положительную или отрицательную
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :param amount: Сумма на которую изменяется баланс. Может быть отрицательной
        :type amount: int
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.balance += amount
            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def change_debt(cls, tg_id: int, new_debt: int):
        """
        Метод для изменения долга на новое значение
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :param new_debt: Новая сумма долга пользователя
        :type new_debt: int
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.debt = new_debt
            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def add_debt(cls, tg_id: int, amount: int):
        """
        Метод для изменения долга на какую-то сумму, положительную или отрицательную
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :param amount: Сумма на которую изменяется долг. Может быть отрицательной
        :type amount: int
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                user.debt += amount
            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def update_paying_status(cls, tg_id: int, is_paying: bool):
        """
        Меняет поле is_paying на новое значение\n
        Функция используется при продлении подписки или при окончании ее срока действия
        
        :param tg_id: ID пользователя Telegram
        :type tg_id: int
        :param is_paying: Новое значение поля is_paying
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user and user.is_paying == is_paying:
                return "No changes"
            elif user:
                user.is_paying = is_paying

            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def get_paying_status(cls, tg_id: int):
        user = await cls.get_user(tg_id=tg_id)
        if user:
            return user.is_paying

    @classmethod
    async def update_subscription_status(cls, tg_id: int, is_subscribed: bool):
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user and user.is_subscribed == is_subscribed:
                return "No changes"
            # if not user.is_paying:
            #     return "User is not paying"

            if user:
                user.is_subscribed = is_subscribed
            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def get_subscription_status(cls, tg_id: int):
        user = await cls.get_user(tg_id=tg_id)
        if user:
            return user.is_subscribed
    
    @classmethod
    async def get_all_users(cls):
        async with async_session() as session:
            users = await session.scalars(select(User).limit(1000))
            return users