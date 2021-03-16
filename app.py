import telebot
from message_manager import MessageManager

from service_files.speeches import bot_service_speeches
from service_files.settings import TOKEN

bot = telebot.TeleBot(TOKEN, threaded=False)

bot.cle

def delete_buttons(chat_id, message_id, text):
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except Exception as e:
        print(repr(e))


def delete_trash(message):
    bot.delete_message(message.chat.id, message.message_id)


def send_message(chat_id, text, markup=None, file_path=None):
    try:
        if not file_path:
            bot.send_message(chat_id, text, reply_markup=markup if markup else None)
        else:
            bot.send_document(chat_id, data=open(file_path, 'rb'), reply_markup=markup)
        return True
    except Exception as e:
        print(repr(e))
        return False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    manager = MessageManager(message.chat.id)
    response = manager.start()
    if not send_message(message.chat.id, response['text'], response['markup']):
        delete_trash(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    message_text = call.message.text
    text = call.data

    delete_buttons(user_id, message_id, message_text)
    manager = MessageManager(user_id)
    response = None
    try:
        response = manager.dispatch(text)
    except Exception as e:
        print(repr(e))

    if not send_message(user_id, response['text'], response['markup'], response['file_path']):
        response = {'text': 'Что-то пошло не так', 'markup': None}
        send_message(user_id, response['text'], markup=None)


def get_file_info_or_error_text(raw):
    if raw.file_size <= 10485760:
        return bot.get_file(raw.file_id)
    else:
        return bot_service_speeches['file_is_too_big'].format(raw.file_size)


def download_file(file_path):
    try:
        file = bot.download_file(file_path)
        return file
    except Exception as e:
        print(repr(e))
        return None


@bot.message_handler(content_types=['video'])
def receiving_video(message):
    raw = message.video
    print(message)
    file_info = get_file_info_or_error_text(raw)
    if type(file_info) == str:
        send_message(message.chat.id, file_info)
        return delete_trash(message)

    file = download_file(file_info.file_path)
    manager = MessageManager(message.chat.id)
    response = manager.dispatch(message.caption, file, file_info)
    if not send_message(message.chat.id, response['text'], response['markup']):
        delete_trash(message)


@bot.message_handler(content_types=['photo'])
def receiving_photo(message):
    raw = message.photo[-1]
    file_info = get_file_info_or_error_text(raw)
    if type(file_info) == str:
        send_message(message.chat.id, file_info)
        return delete_trash(message)

    file = download_file(file_info.file_path)
    manager = MessageManager(message.chat.id)
    response = manager.dispatch(message.caption, file, file_info)
    if not send_message(message.chat.id, response['text'], response['markup']):
        delete_trash(message)


@bot.message_handler(content_types=['audio'])
def receiving_audio(message):
    raw = message.audio
    file_info = get_file_info_or_error_text(raw)
    if type(file_info) == str:
        send_message(message.chat.id, file_info)
        return delete_trash(message)

    file = download_file(file_info.file_path)
    manager = MessageManager(message.chat.id)
    response = manager.dispatch(message.caption, file, file_info)
    if not send_message(message.chat.id, response['text'], response['markup']):
        delete_trash(message)


@bot.message_handler(content_types=['document'])
def receiving_document(message):
    raw = message.document
    file_info = get_file_info_or_error_text(raw)
    if type(file_info) == str:
        send_message(message.chat.id, file_info)
        return delete_trash(message)

    file = download_file(file_info.file_path)
    manager = MessageManager(message.chat.id)
    response = manager.dispatch(message.caption, file, file_info)
    if not send_message(message.chat.id, response['text'], response['markup']):
        delete_trash(message)


@bot.message_handler(func=lambda message: True)
def receiving_messages(message):
    manager = MessageManager(message.chat.id)
    response = manager.dispatch(message.text)
    if not send_message(message.chat.id, response['text'], response['markup'], response['file_path']):
        delete_trash(message)


bot.polling(none_stop=True)

