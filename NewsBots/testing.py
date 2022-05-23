import logging
import pytz
#import fetch
import telegram.ext
import datetime

# from datetime import datetime
# from datetime import time
from fetch import fetcher
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, InlineQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#latest_news = fetch.latest_news_text

user_hour = 13
user_minute = 0
user_time = f'{user_hour}:{user_minute}'
kektext = 'kektext'
#kektext = fetcher.fetch_data()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать! Данный бот присылает новостной "
                                                                    "деск с сайта СнМИ.рф каждый будний день "
                                                                    "по умолчанию "
                                                                    "в 13:00, а также предоставляет доступ к архиву "
                                                                    "новостей.\n"
                                                                    "\n"
                                                                    "Команды\n"
                                                                    "/start - перезапуск бота после его остановки\n"
                                                                    "/archive - получить доступ к архиву\n"
                                                                    "/settime - выбрать время получения новостей\n"
                                                                    "/latest - получить последний выпуск\n"
                                                                    "/stop - остановить бота\n")
    #context.job_queue.stop()
    context.job_queue.start()
    timejob = datetime.time(hour=user_hour, minute=user_minute, tzinfo=pytz.timezone('Europe/Moscow'))
    context.job_queue.run_daily(auto_news, timejob, days=(0, 1, 2, 3, 4), context=update.message.chat_id)
    #context.job_queue.run_repeating(text, 1, context=update.message.chat_id)


def stop(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Бот остановален')
    context.job_queue.stop()
    #context.job_queue.start()


def time(update, context):
    global user_time, user_hour, user_minute
    user_time = update.message.text
    if len(user_time) > 5 or user_time[2] != ':' or int(user_time.split(':')[0]) > 23 or int(user_time.split(':')[1]) > 59:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Пожалуйста введите время в формате ЧЧ:ММ")
    else:
        user_time = update.message.text
        user_time = user_time[:5]
        user_hour = int(user_time.split(':')[0])
        user_minute = int(user_time.split(':')[1])
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Теперь новости будут приходить в {user_time}")
        #context.job_queue.stop()
        context.job_queue.start()
        timejob = datetime.time(hour=user_hour, minute=user_minute, tzinfo=pytz.timezone('Europe/Moscow'))
        context.job_queue.run_daily(auto_news, timejob, days=(0, 1, 2, 3, 4), context=update.message.chat_id)
        #context.job_queue.run_repeating(text, 5, context=update.message.chat_id)


def settime(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, выберете время в формате ЧЧ:ММ "
                                                                    "по Москве\n"
                                                                    "Обращаем внимание - дайджест на сайте снми.рф "
                                                                    "обновляется каждый "
                                                                    "будний день не позднее 13:00")
    context.job_queue.run_once(time, when=0, context=update.message.chat_id)


def latest(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=kektext, parse_mode=telegram.ParseMode.MARKDOWN)
    # if len(latest_news) > 4096:
    #     # for x in range(0, len(latest_news), 4096):
    #         # if latest_news[x + 4095] == "*":
    #         #     latest_news[x + 4096] = ''
    #     context.bot.send_message(chat_id=update.effective_chat.id, text=latest_news[0:4083],
    #                                  parse_mode=telegram.ParseMode.MARKDOWN)
    # else:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text=latest_news,
    #                              parse_mode=telegram.ParseMode.MARKDOWN)

def text(context):
    context.bot.send_message(context.job.context, text='test', disable_notification=False)


def auto_news(context):
    context.bot.send_message(context.job.context, text='kekw',
                             parse_mode=telegram.ParseMode.MARKDOWN)
    # if len(latest_news) > 4096:
    #     for x in range(0, len(latest_news), 4096):
    #         context.bot.send_message(context.job.context, text=latest_news[x:x + 4096],
    #                                  parse_mode=telegram.ParseMode.MARKDOWN)
    # else:
    #     context.bot.send_message(context.job.context, text=latest_news,
    #                              parse_mode=telegram.ParseMode.MARKDOWN)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


#def main():
updater = Updater(token='5293833835:AAEjnJjdkacWHMkWta6FsA7ivtEmMtuEZy0', use_context=True)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
settime_handler = CommandHandler('settime', settime)
dispatcher.add_handler(settime_handler)
latest_handler = CommandHandler('latest', latest)
dispatcher.add_handler(latest_handler)
stop_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stop_handler)
time_handler = MessageHandler(Filters.text & (~Filters.command), time)
dispatcher.add_handler(time_handler)
dispatcher.add_error_handler(error)
updater.start_polling()
updater.idle()


#if __name__ == '__main__':
   # main()
