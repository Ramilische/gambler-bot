from db.models import User

start_message = """
Привет, я телеграм бот, посвященный азартным играм

Здесь можно узнать об этих играх и попробовать поиграть на виртуальной валюте без риска

/balance - узнать баланс и долг по микрозаймам
/roulette - рулетка
/dice - кости
"""


def message_balance(user: User):
    return f'Здравствуйте, {user.first_name}!\nБаланс: {user.balance} фишек\nДолг: {str(user.debt) + " фишек" if user.debt > 0 else "отсутствует"}\n'
