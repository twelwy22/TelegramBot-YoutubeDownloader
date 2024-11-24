import telebot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp
import os
from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)
url_storage = {}

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.reply_to(
        message,
        "👋 Привет! Отправь мне ссылку на видео из Tiktok или Youtube, и я помогу тебе скачать его.\n"
    )

@bot.message_handler(func=lambda message: "tiktok.com" in message.text or "youtube.com" in message.text or "youtu.be" in message.text)
def handle_video_request(message: Message):
    url = message.text.strip()
    unique_id = str(len(url_storage))  
    url_storage[unique_id] = url       
    bot.send_message(
        message.chat.id,
        "Выберите формат загрузки:",
        reply_markup=create_format_buttons(unique_id)
    )

def create_format_buttons(unique_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🎥 Видео", callback_data=f"video|{unique_id}"),
        InlineKeyboardButton("🎵 Аудио", callback_data=f"audio|{unique_id}")
    )
    return markup

@bot.callback_query_handler(func=lambda call: True)
def handle_format_selection(call):
    try:
        action, unique_id = call.data.split('|')
        url = url_storage.get(unique_id)  
        if not url:
            bot.answer_callback_query(call.id, "❌ Ссылка не найдена.")
            return

        bot.answer_callback_query(call.id)
        if action == "video":
            bot.send_message(call.message.chat.id, "⌛ Начинаю загрузку видео...")
            download_and_send_media(call.message.chat.id, url, media_type='video')
        elif action == "audio":
            bot.send_message(call.message.chat.id, "⌛ Начинаю загрузку аудио...")
            download_and_send_media(call.message.chat.id, url, media_type='audio')
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Произошла ошибка: {str(e)}")

def download_and_send_media(chat_id, url, media_type='video'):
    if media_type == 'video':
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': False,
        }
    else:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': False,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as file:
            if media_type == 'video':
                bot.send_video(chat_id, file, caption="🎥 Вот твое видео!")
            else:
                bot.send_audio(chat_id, file, caption="🎵 Вот твое аудио!")
        os.remove(filename)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Произошла ошибка: {str(e)}")
import time
from datetime import timedelta
from stringoptions import BotConfig

if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

        print(f"""
=====================================================
🧑‍💻 Бот запущен успешно!
=====================================================
🤖 Токен бота: {API_TOKEN}
📅 Дата запуска: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}
=====================================================
{BotConfig.COMMANDS}
=====================================================
👤 Владелец: {BotConfig.OWNER}
🔗 Ссылка: {BotConfig.OWNER_LINK}
=====================================================
Бот готов к работе!
=====================================================
""")
    bot.infinity_polling()
