import telebot
import requests
import time

TOKEN = "ТВОЙ_BOT_TOKEN"
GROUP_ID = -1003159585382
ADMIN_USERNAME = "pounlock"

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ---------- PHP API ----------
ADD_ECID_URL = "https://vanciu.atwebpages.com/add_ecid.php"
CHECK_ECID_URL = "https://vanciu.atwebpages.com/check_ecid.php"

# ---------- ЛИМИТ 24 ЧАСА ----------
REGISTER_COOLDOWN = 24 * 60 * 60  # 24 часа
last_register_time = {}  # user_id -> timestamp


def add_ecid(ecid):
    r = requests.get(ADD_ECID_URL, params={"ecid": ecid}, timeout=10)
    return r.json()


def check_ecid(ecid):
    r = requests.get(CHECK_ECID_URL, params={"ecid": ecid}, timeout=10)
    return r.json()


# ---------- Новый пользователь ----------
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
            "💰 Its Full Free\n"
            "📩 Please contact an admin if you have problems!\n\n"
            "Download Links: /download"
        )


# ---------- HELP (с именем) ----------
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
    user_id = message.from_user.id
    username = message.from_user.username or ""

    # --- ЛИМИТ (кроме создателя) ---
    if username.lower() != ADMIN_USERNAME.lower():
        now = time.time()
        last_time = last_register_time.get(user_id)

        if last_time and now - last_time < REGISTER_COOLDOWN:
            remaining = int((REGISTER_COOLDOWN - (now - last_time)) / 3600)
            bot.reply_to(
                message,
                f"⏳ You can register ECID again in ~{remaining} hour(s)"
            )
            return

    # --- PHP регистрация ---
    try:
        result = add_ecid(ecid)
    except:
        bot.reply_to(message, "❌ Server error. Try later.")
        return

    if result["status"] == "success":
        last_register_time[user_id] = time.time()
        bot.reply_to(message, f"✅ ECID `{ecid}` registered")

    elif result["status"] == "exists":
        bot.reply_to(message, f"⚠️ ECID `{ecid}` already registered")

    else:
        bot.reply_to(message, "❌ Error registering ECID")


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

    try:
        result = check_ecid(ecid)
    except:
        bot.reply_to(message, "❌ Server error")
        return

    if result["status"] == "exists":
        bot.reply_to(message, f"✅ ECID `{ecid}` is registered")
    else:
        bot.reply_to(message, f"❌ ECID `{ecid}` not found")


# ---------- DOWNLOAD ----------
@bot.message_handler(commands=["download"])
def download(message):
    bot.reply_to(
        message,
        "📥 Download link:\n"
        "👉 https://www.mediafire.com/file/sgw0wxk4fn6xgb8/PO+Tools+A12+.zip/file"
    )


bot.polling(none_stop=True)

