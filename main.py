import telebot
import sqlite3
from datetime import datetime

TOKEN = "8495656409:AAHK9Ll3JnKscLVQt1Iw0VF6qMT69iQHfEg"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  

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
    reply(message, "🎉 Welcome to HG Tools! /n
 Version 1.0 is now live!
✅ Fully compatible with Windows
✅ Supports A12+ devices with iOS 15 through iOS 26.1
✅ Automatically blocks OTA updates
💰 Its Full Free
📩 Please contact an admin is u have problems!
Donwload Links: /download")

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
        reply(message, "❌ Format:\n`/register <ECID>`")
        return

    ecid = parts[1].strip()
    user_id = message.from_user.id
    username = message.from_user.username or ""

    cursor.execute("SELECT ecid FROM ecid_log WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        reply(message, "⚠️ ECID already registered")
        return

    cursor.execute(
        "INSERT INTO ecid_log (user_id, username, ecid, registered_at) VALUES (?, ?, ?, ?)",
        (user_id, username, ecid, datetime.now().isoformat())
    )
    conn.commit()

    reply(message, f"✅ ECID `{ecid}` registered.")

@bot.message_handler(commands=['download'])
def download(message):
    reply(message, "📥 Download link:\n👉 https://www.mediafire.com/file/sgw0wxk4fn6xgb8/PO+Tools+A12+.zip/file")

bot.polling(none_stop=True)
