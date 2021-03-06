import logging
import time

import requests
import sentry_sdk
from envparse import env
from telegram import Bot, ParseMode, TelegramError

from models import CashRemain, Chat, db

env.read_envfile()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

sentry_sdk.init(env("SENTRY_DSN", default=None))

bot = Bot(token=env("TELEGRAM_BOT_TOKEN"))
currency = "USD"


def get_clusters():

    # Thats a msk location for testing
    # !msk = {
    # !    "bottomLeft": {"lat": 55.77128972923776, "lng": 37.09503560017758},
    # !    "topRight": {"lat": 55.960486265455394, "lng": 37.380680131427575},
    # !}

    khv = {
        "bottomLeft": {"lat": 48.35559027141748, "lng": 134.91545706263585},
        "topRight": {"lat": 48.57933649214029, "lng": 135.20110159388588},
    }

    response = requests.post(
        "https://api.tinkoff.ru/geo/withdraw/clusters",
        headers={"Content-Type": "application/json"},
        json={
            "bounds": khv,
            "filters": {
                "banks": ["tcs"],
                "showUnavailable": False,
                "currencies": ["USD"],
            },
            "zoom": 12,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["payload"]["clusters"]


@db.atomic()
def refill():
    CashRemain.delete().execute()

    for cluster in get_clusters():
        for point in cluster["points"]:
            address = point["address"]
            amount = None
            for limit in point["limits"]:
                if limit["currency"] == currency:
                    amount = limit["amount"]
                    break

            if amount:
                logging.log(logging.DEBUG, f"Got {address}: {amount} {currency}")
                CashRemain.create(
                    address=address,
                    amount=amount,
                    currency=currency,
                )


def get_remains() -> dict:
    return dict(
        CashRemain.select(CashRemain.address, CashRemain.amount)
        .order_by(CashRemain.amount.desc())
        .tuples()
    )


def make_diff_message(before: dict, after: dict) -> str:
    messages = []

    for atm in before:
        if atm not in after:
            after[atm] = 0

    for atm, amount in after.items():
        if atm not in before or before[atm] < after[atm]:
            messages.append(f"???? O???????????? <b>{amount}</b> {currency} ???? {atm}")
        elif before[atm] > after[atm]:
            messages.append(f"???? O????????????: <b>{amount}</b> {currency} ???? {atm}")

    return "\n".join(messages)


def broadcast(message: str):
    for (chat_id,) in Chat.select(Chat.chat_id).tuples():
        try:
            bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
        except TelegramError:
            logging.error(f"Error while sending message to {chat_id}: {message}")


if __name__ == "__main__":

    while True:

        before = get_remains()
        refill()
        after = get_remains()

        if message := make_diff_message(before, after):
            logging.log(logging.DEBUG, f"Broadcasting: {message}")
            broadcast(message)
        else:
            logging.log(logging.DEBUG, "Nothing to broadcast")

        time.sleep(120)
