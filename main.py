import telebot
import sqlite3
from datetime import datetime

TOKEN = "ТУТ_ТОКЕН"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  # 🔥 просто убираем аргумент

conn = sqlite3.connect("ecid.db", check_same_thread=False)
cursor = conn.cursor()

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

def reply(message, text):
    name = message.from_user.first_name or "User"
    bot.send_message(
        message.chat.id,
        f"*{name}* 👋 {text}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['start'])
def start(message):
    reply(message, "Добро пожаловать!\nНапиши /help")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    reply(
        message,
        "Bot Commands\n\n"
        "• Register ECID:\n`/register <ECID>`\n\n"
        "• Download link:\n`/download`\n\n"
        "• Show help:\n`/help`"
    )

@bot.message_handler(commands=['register'])
def register(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        reply(message, "❌ Формат:\n`/register <ECID>`")
        return

    ecid = parts[1].strip()
    user_id = message.from_user.id
    username = message.from_user.username or ""

    cursor.execute("SELECT ecid FROM ecid_log WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        reply(message, "⚠️ ECID уже зарегистрирован.")
        return

    cursor.execute(
        "INSERT INTO ecid_log (user_id, username, ecid, registered_at) VALUES (?, ?, ?, ?)",
        (user_id, username, ecid, datetime.now().isoformat())
    )
    conn.commit()

    reply(message, f"✅ ECID `{ecid}` сохранён.")

@bot.message_handler(commands=['download'])
def download(message):
    reply(message, "📥 Download link:\n👉 https://www.chatgpt.com")

bot.polling(none_stop=True)
