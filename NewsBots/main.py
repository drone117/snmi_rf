import logging
import pytz
import fetch
import telegram.ext
import datetime

from telegram.ext import Updater
from telegram.ext import CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

latest_news = fetch.latest_news_text

user_hour = 13
user_minute = 0
user_time = f'{user_hour}:{user_minute}'


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать! Данный бот присылает новостной "
                                                                    "деск с сайта СнМИ.рф каждый будний день "
                                                                    "по умолчанию "
                                                                    "в 13:00, а также предоставляет доступ к архиву "
                                                                    "новостей.\n"
                                                                    "\n"
                                                                    "Команды\n"
                                                                    "/start - перезапуск бота после его остановки\n"
                                                                    "/latest - получить последний выпуск\n")
    timejob = datetime.time(hour=user_hour, minute=user_minute, tzinfo=pytz.timezone('Europe/Moscow'))
    context.job_queue.run_daily(auto_news, timejob, days=(0, 1, 2, 3, 4), context=update.message.chat_id)


def latest(update, context):
    if len(latest_news) > 4096:
        for x in range(0, len(latest_news), 4096):
            context.bot.send_message(chat_id=update.effective_chat.id, text=latest_news[x:x + 4096],
                                     parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=latest_news,
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def auto_news(context):

    if len(latest_news) > 4096:
        for x in range(0, len(latest_news), 4096):
            context.bot.send_message(context.job.context, text=latest_news[x:x + 4096],
                                     parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.send_message(context.job.context, text=latest_news,
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token='5381998359:AAH-fTcEBFzbuvGc4hHDmqbaKpS3PZFcOmQ', use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    latest_handler = CommandHandler('latest', latest)
    dispatcher.add_handler(latest_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
