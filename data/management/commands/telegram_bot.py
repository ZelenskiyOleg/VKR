from datetime import datetime

import environ
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

from django.conf import settings

JOURNAL_ENDPOINT = "http://localhost:8000/data/journal/"
DJANGO_ENDPOINT = "http://localhost:8000/data/receive_photo/"

def journal_command(update: Update, context: CallbackContext):
    try:
        date_str = context.args[0]
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        update.message.reply_text(f'Вы указали дату: {date_str}')
        response = requests.post(JOURNAL_ENDPOINT,data={'date':date_str, 'userid':update.message.from_user.id})
    except(IndexError, ValueError):
        update.message.reply_text(f'Неправильный формат даты. Используйте YYYY-mm-dd')



def handle_photo(update, context):
    try:
        update.message.reply_text("Получена фотография. Обрабатывается...")
        photo_obj = update.message.photo[-1]
        photo_file = photo_obj.get_file()
        photo_data = photo_file.download_as_bytearray()
        data = {'userid': update.message.from_user.id}
        response = requests.post(DJANGO_ENDPOINT, files={'photo': ('photo.jpg', photo_data, 'image/jpeg')}, data=data)


        if response.status_code == 200:
            update.message.reply_text("Фотография успешно обработана.")
        else:
            update.message.reply_text("На фото нет студентов, занесенных в БД")

    except Exception as e:
        update.message.reply_text(f"Произошла ошибка: {e}")


def main():
    updater = Updater('7047307763:AAHfBNSGPaZePzmRGfHgSu8-sFUtqvN_M1A', use_context=True)
    dispatcher = updater.dispatcher

    photo_handler = MessageHandler(Filters.photo, handle_photo)
    dispatcher.add_handler(photo_handler)
    updater.dispatcher.add_handler(CommandHandler('journal', journal_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

