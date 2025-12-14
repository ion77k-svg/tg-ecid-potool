import telebot
import requests

TOKEN = "8495656409:AAHK9Ll3JnKscLVQt1Iw0VF6qMT69iQHfEg"
GROUP_ID = -1003159585382
ADMIN_USERNAME = "pounlock"

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ---------- PHP API ----------
ADD_ECID_URL = "https://vanciu.atwebpages.com/add_ecid.php"
CHECK_ECID_URL = "https://vanciu.atwebpages.com/check_ecid.php"


def add_ecid(ecid, user_id, is_admin=False):
    try:
        r = requests.get(
            ADD_ECID_URL,
            params={
                "ecid": ecid,
                "user_id": user_id,
                "admin": "1" if is_admin else "0"
            },
            timeout=10
        )
        return r.json()
    except:
        return {"status": "error"}


def check_ecid(ecid):
    try:
        r = requests.get(CHECK_ECID_URL, params={"ecid": ecid}, timeout=10)
        return r.json()
    except:
        return {"status": "error"}


# ---------- NEW USER ----------
@bot.message_handler(content_types=["new_chat_members"])
def welcome(message):
    for user in message.new_chat_members:
        name = user.first_name or "User"
        bot.send_message(
            message.chat.id,
            f"*{name}* 👋\n\n"
            "🎉 Welcome to HG Tools!\n\n"
            "Version 1.0 is now live!\n"
            "✅ Fully compatible with Windows\n"
            "✅ Supports A12+ devices with iOS 15 through iOS 26.1\n"
            "✅ Automatically blocks OTA updates\n"
            "💰 It's fully free\n"
            "📩 Contact an admin if you have issues!\n\n"
            "Download Links: /download"
        )


# ---------- HELP ----------
@bot.message_handler(commands=["help"])
def help_cmd(message):
    name = message.from_user.first_name or "User"
    bot.send_message(
        message.chat.id,
        f"*{name}* 👋\n\n"
        "📌 *Bot Commands*\n\n"
        "• `/register ECID`\n"
        "• `/check ECID`\n"
        "• `/download`\n"
        "• `/help`"
    )


# ---------- REGISTER ----------
@bot.message_handler(commands=["register"])
def register(message):
    if message.chat.id != GROUP_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "❌ Format:\n`/register ECID`")
        return

    ecid = parts[1].strip().upper()
    user = message.from_user
    is_admin = (user.username or "").lower() == ADMIN_USERNAME.lower()

    result = add_ecid(ecid, user.id, is_admin)

    if result["status"] == "success":
        bot.reply_to(message, f"✅ ECID `{ecid}` registered")
    elif result["status"] == "exists":
        bot.reply_to(message, f"⚠️ ECID `{ecid}` already registered")
    elif result["status"] == "limit":
        bot.reply_to(message, "⏳ Limit reached: 1 ECID per 24 hours")
    else:
        bot.reply_to(message, "❌ Registration error")


# ---------- CHECK ----------
@bot.message_handler(commands=["check"])
def check(message):
    if message.chat.id != GROUP_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "❌ Format:\n`/check ECID`")
        return

    ecid = parts[1].strip().upper()
    result = check_ecid(ecid)

    if result["status"] == "exists":
        bot.reply_to(message, f"✅ ECID `{ecid}` is registered")
    else:
        bot.reply_to(message, f"❌ ECID `{ecid}` not registered")


# ---------- DOWNLOAD ----------
@bot.message_handler(commands=["download"])
def download(message):
    bot.reply_to(
        message,
        "📥 Download link:\n"
        "👉 https://www.mediafire.com/file/sgw0wxk4fn6xgb8/PO+Tools+A12+.zip/file"
    )


bot.polling(none_stop=True)
