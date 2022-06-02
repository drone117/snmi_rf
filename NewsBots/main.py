import logging
import pytz
import fetch
import telegram.ext
import datetime

from telegram.constants import ParseMode
from fetch import fetcher
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackContext, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

user_hour = 13
user_minute = 0
user_time = f'{user_hour}:{user_minute}'


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Добро пожаловать! Данный бот присылает новостной "
                                    "деск с сайта СнМИ.рф каждый будний день "
                                    "по умолчанию в 13:00.\n"
                                    "Для того, чтобы изменить время получения новостей, "
                                    "введите требуемое время в формате ЧЧ:ММ"
                                    "\n"
                                    "Команды\n"
                                    "/start - перезапустить бота\n"
                                    "/stop - остановить бота\n"
                                    "/latest - получить последний выпуск\n")
    global user_time, user_hour, user_minute
    user_hour = 13
    user_minute = 0
    user_time = f'{user_hour}:{user_minute}'
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    name = update.effective_chat.full_name
    timejob = datetime.time(hour=user_hour, minute=user_minute, tzinfo=pytz.timezone('Europe/Moscow'))
    context.job_queue.run_daily(auto_news, timejob, days=(0, 1, 2, 3, 4), context=name,
                                chat_id=update.message.chat_id)


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def latest(update: Update, context: CallbackContext):
    await update.effective_chat.send_message(text=fetcher.fetch_date(),
                                             parse_mode=ParseMode.MARKDOWN)
    for keys in fetcher.fetch_data():
        if len(fetcher.fetch_data()[keys]) > 4096:
            await update.effective_chat.send_message(text=keys + '\n', parse_mode=ParseMode.MARKDOWN)
            for x in range(0, len(fetcher.fetch_data()[keys]), 4096):
                await update.effective_chat.send_message(text=fetcher.fetch_data()[keys][x:x + 4096],
                                                         parse_mode=ParseMode.MARKDOWN)
        else:
            await update.effective_chat.send_message(text=keys + '\n' + fetcher.fetch_data()[keys],
                                                     parse_mode=ParseMode.MARKDOWN)


async def auto_news(context: CallbackContext):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=fetcher.fetch_date(),
                                   parse_mode=ParseMode.MARKDOWN)
    for keys in fetcher.fetch_data():
        if len(fetcher.fetch_data()[keys]) > 4096:
            await context.bot.send_message(chat_id=job.chat_id,
                                           text=keys + '\n', parse_mode=ParseMode.MARKDOWN)
            for x in range(0, len(fetcher.fetch_data()[keys]), 4096):
                await context.bot.send_message(chat_id=job.chat_id,
                                               text=fetcher.fetch_data()[keys][x:x + 4096],
                                               parse_mode=ParseMode.MARKDOWN)
        else:
            await context.bot.send_message(chat_id=job.chat_id, text=keys + '\n' + fetcher.fetch_data()[keys],
                                           parse_mode=ParseMode.MARKDOWN)


async def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def time(update: Update, context: CallbackContext):
    global user_time, user_hour, user_minute
    user_time = update.message.text
    if len(user_time) > 5 or user_time[2] != ':' or int(user_time.split(':')[0]) > 23 or int(
            user_time.split(':')[1]) > 59:
        await update.message.reply_text("Пожалуйста введите время в формате ЧЧ:ММ")
    else:
        user_time = update.message.text
        user_time = user_time[:5]
        user_hour = int(user_time.split(':')[0])
        user_minute = int(user_time.split(':')[1])
        await update.message.reply_text(f"Теперь новости будут приходить в {user_time}")
        chat_id = update.effective_message.chat_id
        job_removed = remove_job_if_exists(str(chat_id), context)
        name = update.effective_chat.full_name
        timejob = datetime.time(hour=user_hour, minute=user_minute, tzinfo=pytz.timezone('Europe/Moscow'))
        context.job_queue.run_daily(auto_news, timejob, days=(0, 1, 2, 3, 4), context=name,
                                    chat_id=update.message.chat_id)


async def stop(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Бот остановлен." if job_removed else "Бот не запущен."
    await update.message.reply_text(text)


def main():
    application = ApplicationBuilder().token('5381998359:AAH-fTcEBFzbuvGc4hHDmqbaKpS3PZFcOmQ').build()
    start_handler = CommandHandler('start', start)
    latest_handler = CommandHandler('latest', latest)
    stop_handler = CommandHandler('stop', stop)
    time_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), time)
    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(latest_handler)
    application.add_handler(time_handler)
    application.add_error_handler(error)
    application.run_polling()


if __name__ == '__main__':
    main()
