import logging
import pytz
import fetch
import telegram.ext


from datetime import datetime
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, InlineQueryHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

latest_news = fetch.latest_news_text


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать! Данный бот присылает новостной "
                                                                    "деск с сайта СнМИ.рф каждый день по умолчанию "
                                                                    "в 13:00, а также предоставляет доступ к архиву "
                                                                    "новостей.\n"
                                                                    "\n"
                                                                    "Команды\n"
                                                                    "/archive - получить доступ к архиву\n"
                                                                    "/settime - выбрать время получения новостей\n"
                                                                    "/latest - получить последний выпуск\n")


def settime(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, выберете время")
    user_time = "13:00"
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Теперь новости будут приходить в {user_time}")


def latest(update, context):
    if len(latest_news) > 4096:
        for x in range(0, len(latest_news), 4096):
            context.bot.send_message(chat_id=update.effective_chat.id, text=latest_news[x:x+4096],
                                     parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=latest_news,
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def auto_news(context):
    context.bot.send_message(context.job.context, text=f"{latest_news}")


def time(update, context):
    context.job_queue.run_daily(auto_news, datetime.time(hour=17, minute=19,
                                                         tzinfo=pytz.timezone('Europe/Moscow')),
                                days=(0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)


def timefunc():
    now = datetime.now()
    current_month = now.month
    current_day = now.day
    current_time = now.strftime("%H:%M:%S")
#     if current_time == "16:30:00":
#         return True
#     else:
#         return False


def main():
    updater = Updater(token='5381998359:AAH-fTcEBFzbuvGc4hHDmqbaKpS3PZFcOmQ', use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    settime_handler = CommandHandler('settime', settime)
    dispatcher.add_handler(settime_handler)
    latest_handler = CommandHandler('latest', latest)
    dispatcher.add_handler(latest_handler)
    time_handler = MessageHandler(Filters.text, time)
    dispatcher.add_handler(time_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
