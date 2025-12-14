import telebot
import requests
import re
import urllib3

# -------------------- Настройки --------------------
TOKEN = "8495656409:AAHK9Ll3JnKscLVQt1Iw0VF6qMT69iQHfEg"
GROUP_ID = -1003159585382
ADMIN_USERNAME = "pounlock"

bot = telebot.TeleBot(TOKEN)

# -------------------- SSL --------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------- PHP API --------------------
ADD_ECID_URL = "https://vanciu.atwebpages.com/add_ecid.php"
CHECK_ECID_URL = "https://vanciu.atwebpages.com/check_ecid.php"

# -------------------- Экранирование Markdown --------------------
def escape_markdown(text):
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# -------------------- Работа с API --------------------
def add_ecid(ecid, user_id, is_admin=False):
    try:
        r = requests.get(
            ADD_ECID_URL,
            params={"ecid": ecid, "user_id": user_id, "admin": "1" if is_admin else "0"},
            timeout=10,
            verify=False
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_ecid(ecid):
    try:
        r = requests.get(
            CHECK_ECID_URL,
            params={"ecid": ecid},
            timeout=10,
            verify=False
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# -------------------- NEW USER --------------------
@bot.message_handler(content_types=["new_chat_members"])
def welcome(message):
    for user in message.new_chat_members:
        name = user.first_name or "User"
        bot.send_message(
            message.chat.id,
            f"*{escape_markdown(name)}* 👋\n\n"
            "🎉 Welcome to HG Tools!\n"
            "Version 1.0 is now live!\n"
            "✅ Fully compatible with Windows\n"
            "✅ Supports A12+ devices with iOS 15 through iOS 26.1\n"
            "✅ Automatically blocks OTA updates\n"
            "💰 It's fully free\n"
            "📩 Contact an admin if you have issues!\n\n"
            "Download Links: /download",
            parse_mode="Markdown"
        )

# -------------------- HELP --------------------
@bot.message_handler(commands=["help"])
def help_cmd(message):
    name = message.from_user.first_name or "User"
    bot.send_message(
        message.chat.id,
        f"*{escape_markdown(name)}* 👋\n\n"
        "📌 *Bot Commands*\n\n"
        "• `/register ECID`\n"
        "• `/check ECID`\n"
        "• `/download`\n"
        "• `/help`",
        parse_mode="Markdown"
    )

# -------------------- REGISTER --------------------
@bot.message_handler(commands=["register"])
def register(message):
    if message.chat.id != GROUP_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "❌ Format:\n/register ECID")
        return

    ecid = parts[1].strip().upper()
    user = message.from_user
    is_admin = (user.username or "").lower() == ADMIN_USERNAME.lower()

    result = add_ecid(ecid, user.id, is_admin)

    status = result.get("status", "error")
    message_text = escape_markdown(result.get("message", "Unknown error"))

    if status == "success":
        bot.reply_to(message, f"✅ Registered {escape_markdown(ecid)} succesfully!")
    elif status == "exists":
        bot.reply_to(message, f"⚠️ ECID already Registered!")
    elif status == "limit":
        bot.reply_to(message, f"⏳ U can Regiser **1 ECID per Day**")
    elif status == "error":
        bot.reply_to(message, f"❌ Registration error: {message_text}")
    else:
        bot.reply_to(message, f"❌ Unknown status: {message_text}")

# -------------------- CHECK --------------------
@bot.message_handler(commands=["check"])
def check(message):
    if message.chat.id != GROUP_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "❌ Format:\n/check ECID")
        return

    ecid = parts[1].strip().upper()
    result = check_ecid(ecid)

    status = result.get("status", "error")
    message_text = escape_markdown(result.get("message", ""))

    if status == "exists":
        bot.reply_to(message, f"✅ ECID `{escape_markdown(ecid)}` is registered")
    elif status == "error":
        bot.reply_to(message, f"❌ Server error: {message_text}")
    else:
        bot.reply_to(message, f"❌ ECID `{escape_markdown(ecid)}` not found")

# -------------------- DOWNLOAD --------------------
@bot.message_handler(commands=["download"])
def download(message):
    bot.reply_to(
        message,
        "📥 Download link:\n"
        "👉 https://www.mediafire.com/file/sgw0wxk4fn6xgb8/PO+Tools+A12+.zip/file"
    )

bot.polling(none_stop=True)
