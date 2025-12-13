import telebot
import sqlite3
from datetime import datetime, timedelta

TOKEN = "8495656409:AAHK9Ll3JnKscLVQt1Iw0VF6qMT69iQHfEg"
CREATOR_USERNAME = "pounlock"  # твой юзернейм без @

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  

# Подключение к базе
conn = sqlite3.connect("ecid.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если её нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS ecid_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    ecid TEXT,
    registered_at TEXT
)
""")
conn.commit()

# Универсальная функция для ответа
def reply(message, text):
    name = message.from_user.first_name or "User"
    bot.send_message(
        message.chat.id,
        f"*{name}* 👋 {text}",
        parse_mode="Markdown"
    )

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    reply(message, (
        "🎉 Welcome to HG Tools!\n"
        "Version 1.0 is now live!\n"
        "✅ Fully compatible with Windows\n"
        "✅ Supports A12+ devices with iOS 15 through iOS 26.1\n"
        "✅ Automatically blocks OTA updates\n"
        "💰 It's fully free\n"
        "📩 Please contact an admin if you have problems!\n"
        "Download Links: /download"
    ))

# Команда /help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    reply(
        message,
        "Bot Commands\n\n"
        "• Register ECID:\n`/register <ECID>`\n\n"
        "• Check ECID:\n`/check <ECID>`\n\n"
        "• Download link:\n`/download`\n\n"
        "• Show help:\n`/help`"
    )

# Команда /register
@bot.message_handler(commands=['register'])
def register(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        reply(message, "❌ Format:\n`/register <ECID>`")
        return

    ecid = parts[1].strip()
    user_id = message.from_user.id
    username = message.from_user.username or ""

    # Проверка, если ECID уже зарегистрирован
    cursor.execute("SELECT ecid FROM ecid_log WHERE user_id = ?", (user_id,))
    if cursor.fetchone() and username != CREATOR_USERNAME:
        # Проверка ограничения 1 регистрация в 24 часа
        cursor.execute("SELECT registered_at FROM ecid_log WHERE user_id = ? ORDER BY registered_at DESC LIMIT 1", (user_id,))
        last_time_str = cursor.fetchone()[0]
        last_time = datetime.fromisoformat(last_time_str)
        if datetime.now() - last_time < timedelta(hours=24):
            reply(message, "⚠️ Register only 1 ECID in 24 hours")
            return

    # Проверка, что ECID уникален
    cursor.execute("SELECT ecid FROM ecid_log WHERE ecid = ?", (ecid,))
    if cursor.fetchone():
        reply(message, "⚠️ ECID already registered")
        return

    # Вставка в базу
    cursor.execute(
        "INSERT INTO ecid_log (user_id, username, ecid, registered_at) VALUES (?, ?, ?, ?)",
        (user_id, username, ecid, datetime.now().isoformat())
    )
    conn.commit()

    reply(message, f"✅ ECID `{ecid}` registered successfully.")

# Команда /check
@bot.message_handler(commands=['check'])
def check_ecid(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        reply(message, "❌ Format:\n`/check <ECID>`")
        return

    ecid = parts[1].strip()

    cursor.execute("SELECT username, registered_at FROM ecid_log WHERE ecid = ?", (ecid,))
    row = cursor.fetchone()

    if row:
        username, registered_at = row
        reply(message, f"ℹ️ ECID `{ecid}` is registered ")
    else:
        reply(message, f"✅ ECID `{ecid}` is not registered ")

# Команда /download
@bot.message_handler(commands=['download'])
def download(message):
    reply(message, "📥 Download link:\n👉 https://www.mediafire.com/file/sgw0wxk4fn6xgb8/PO+Tools+A12+.zip/file")

# Запуск бота
bot.polling(none_stop=True)
