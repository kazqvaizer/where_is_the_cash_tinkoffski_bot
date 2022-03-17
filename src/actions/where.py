from datetime import timedelta

from models import CashRemain

from .base import Action


class WhereAction(Action):
    def do(self):
        remains = list(CashRemain.select().order_by(CashRemain.amount.desc()))

        if len(remains) == 0:
            self.reply("Валюты нигде нет. Добро пожаловать в Союз.")
            return

        availability_date = remains[0].created
        availability_date += timedelta(hours=10)  # Vladivostok time
        availability_date = availability_date.strftime("%Y-%m-%d %H:%M:%S")

        self.reply(f"Вот, все что есть на {availability_date}\n\n")
        self.reply(
            "\n".join(
                [
                    f"<b>{remain.amount}</b> {remain.currency}: {remain.address}"
                    for remain in remains
                ]
            )
        )
