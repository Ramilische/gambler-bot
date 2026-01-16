from asyncio import run
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from routers import games, start

load_dotenv('.env/creds.env')
BOT_TOKEN = str(getenv('BOT_TOKEN'))


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_routers(
        start.router,
        games.router,
    )
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    run(main())
