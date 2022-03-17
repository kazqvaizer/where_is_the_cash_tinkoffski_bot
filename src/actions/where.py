from models import CashRemain

from .base import Action


class WhereAction(Action):
    def do(self):
        remains = CashRemain.select().order_by(CashRemain.amount.desc())

        if len(remains) == 0:
            self.reply("Валюты нигде нет. Добро пожаловать в Союз.")
            return

        self.reply("Вот, все что есть:\n\n")
        self.reply(
            "\n".join(
                [
                    f"<b>{remain.amount}</b> {remain.currency}: {remain.address}"
                    for remain in remains
                ]
            )
        )
