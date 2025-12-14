import telebot
import sqlite3
from datetime import datetime, timedelta

TOKEN = "8495656409:AAHK9Ll3JnKscLVQt1Iw0VF6qMT69iQHfEg"
GROUP_ID = -1003159585382
OWNER_USERNAME = "pounlock"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# ================= DATABASE =================
conn = sqlite3.connect("ecid.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ecids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ecid TEXT UNIQUE,
    registered_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    last_register TEXT
)
""")

conn.commit()

# ================= HELPERS =================
def is_owner(message):
    return message.from_user.username == OWNER_USERNAME

def in_group(message):
    return message.chat.id == GROUP_ID

def safe_reply(chat_id, text, message_id=None, parse_mode=None):
    try:
        bot.send_message(
            chat_id,
            text,
            reply_to_message_id=message_id,
            parse_mode=parse_mode
        )
    except Exception:
        bot.send_message(
            chat_id,
            text,
            parse_mode=parse_mode
        )

# ================= WELCOME =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    if not in_group(message):
        return

    for user in message.new_chat_members:
        name = user.first_name or "User"

        bot.send_message(
            message.chat.id,
            f"""🎉 Welcome to HG Tools, *{name}*! 👋

Version 1.0 is now live!
✅ Fully compatible with Windows
✅ Supports A12+ devices with iOS 15 through iOS 26.1
✅ Automatically blocks OTA updates
💰 Its Full Free
📩 Please contact an admin if you have problems!

Download Links: /download
""",
            parse_mode="Markdown"
        )

# ================= HELP =================
@bot.message_handler(commands=['help'])
def help_cmd(message):
    if not in_group(message):
        return

    name = message.from_user.first_name or "User"

    bot.send_message(
        message.chat.id,
        f"""👋 *{name}*

🖐 Bot commands:

• Register ECID:
`/register <ECID>`

• Check ECID:
`/check <ECID>`

• Download:
`/download`
""",
        parse_mode="Markdown"
    )

# ================= REGISTER =================
@bot.message_handler(commands=['register'])
def register(message):
    if not in_group(message):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        safe_reply(
            message.chat.id,
            "❌ Format:\n`/register <ECID>`",
            message.message_id,
            parse_mode="Markdown"
        )
        return

    ecid = parts[1].strip()
    user_id = message.from_user.id

    # 24h limit (except owner)
    if not is_owner(message):
        cursor.execute("SELECT last_register FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            last_time = datetime.fromisoformat(row[0])
            if datetime.now() - last_time < timedelta(hours=24):
                safe_reply(
                    message.chat.id,
                    "⏳ U can register only **1 ECID per 24 hours**.",
                    message.message_id,
                    parse_mode="Markdown"
                )
                return

    # duplicate ECID check
    cursor.execute("SELECT ecid FROM ecids WHERE ecid=?", (ecid,))
    if cursor.fetchone():
        safe_reply(
            message.chat.id,
            "⚠️ This ECID is already registered.",
            message.message_id
        )
        return

    # insert ECID
    cursor.execute(
        "INSERT INTO ecids (ecid, registered_at) VALUES (?, ?)",
        (ecid, datetime.now().isoformat())
    )

    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, last_register) VALUES (?, ?)",
        (user_id, datetime.now().isoformat())
    )

    conn.commit()

    safe_reply(
        message.chat.id,
        f"✅ Registered `{ecid}` successfully!",
        message.message_id,
        parse_mode="Markdown"
    )

# ================= CHECK =================
@bot.message_handler(commands=['check'])
def check_ecid(message):
    if not in_group(message):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        safe_reply(
            message.chat.id,
            "❌ Format:\n`/check <ECID>`",
            message.message_id,
            parse_mode="Markdown"
        )
        return

    ecid = parts[1].strip()

    cursor.execute("SELECT ecid FROM ecids WHERE ecid=?", (ecid,))
    exists = cursor.fetchone() is not None

    safe_reply(
        message.chat.id,
        "✅ ECID is registered." if exists else "❌ ECID not registered.",
        message.message_id
    )

# ================= DOWNLOAD =================
@bot.message_handler(commands=['download'])
def download(message):
    if not in_group(message):
        return

    safe_reply(
        message.chat.id,
        "📥 Download:\n👉 https://www.mediafire.com/",
        message.message_id
    )

# ================= START =================
bot.polling(none_stop=True)
