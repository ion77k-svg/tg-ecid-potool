import telebot
import sqlite3
from datetime import datetime, timedelta

TOKEN = "8495656409:AAHK9Ll3JnKscLVQt1Iw0VF6qMT69iQHfEg"
GROUP_ID = -1003159585382  
OWNER_USERNAME = "pounlock" 

bot = telebot.TeleBot(TOKEN)


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

def can_register(user_id, username):
    if username == OWNER_USERNAME:
        return True  
    cursor.execute(
        "SELECT registered_at FROM ecid_log WHERE user_id = ? ORDER BY registered_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        return True
    last_time = datetime.fromisoformat(row[0])
    return datetime.now() - last_time > timedelta(hours=24)

@bot.message_handler(commands=['start'])
def start(message):
    reply(message, (
        "🎉 Welcome to HG Tools!\n"
        "Version 1.0 is now live!
        "✅ Fully compatible with Windows
        "✅ Supports A12+ devices with iOS 15 through iOS 26.1
        "✅ Automatically blocks OTA updates
        "💰 It's Full Free
        "📩 Please contact an admin if you have problems!
        "Download Links: /download"
    ))

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

@bot.message_handler(commands=['register'])
def register(message):
    # Проверка чата
    if message.chat.id != GROUP_ID:
        reply(message, "❌ U not allowed to register here!")
        return

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

   
    if not can_register(user_id, username):
        reply(message, "⏳ U can register only 1 ECID per Day")
        return

    cursor.execute(
        "INSERT INTO ecid_log (user_id, username, ecid, registered_at) VALUES (?, ?, ?, ?)",
        (user_id, username, ecid, datetime.now().isoformat())
    )
    conn.commit()
    reply(message, f"✅ ECID `{ecid}` succesfuly registered.")

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
        reply(message, f"🔎 ECID `{ecid}` already registered")
    else:
        reply(message, f"❌ ECID `{ecid}` is not registered")

@bot.message_handler(commands=['download'])
def download(message):
    reply(message, "📥 Download link:\n👉 https://www.mediafire.com/file/sgw0wxk4fn6xgb8/PO+Tools+A12+.zip/file")

bot.infinity_polling()

