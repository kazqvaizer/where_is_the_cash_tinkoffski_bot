import logging

import sentry_sdk
from envparse import env
from telegram.ext import CommandHandler, Updater

from actions import StartAction, WhereAction

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


env.read_envfile()

sentry_sdk.init(env("SENTRY_DSN", default=None))

updater = Updater(token=env("TELEGRAM_BOT_TOKEN"), use_context=True)


def define_routes():
    add_handler = updater.dispatcher.add_handler

    add_handler(CommandHandler("start", StartAction.run_as_callback))
    add_handler(CommandHandler("help", StartAction.run_as_callback))
    add_handler(CommandHandler("where", WhereAction.run_as_callback))


if __name__ == "__main__":
    define_routes()
    updater.start_polling()
