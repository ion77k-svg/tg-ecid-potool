import telebot
import requests
import re
import urllib3
import time

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
    if not ecid or not user_id:
        return {"status": "error", "message": "Missing parameters"}
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
    if not ecid:
        return {"status": "error", "message": "Missing ECID"}
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
last_register_time = {}  # user_id -> timestamp
COOLDOWN = 24 * 60 * 60  # 24 часа

@bot.message_handler(commands=["register"])
def register(message):
    if message.chat.id != GROUP_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "❌ Format:\n/register ECID")
        return

    ecid = parts[1].strip().upper()

    # ---------- Проверка формата ECID ----------
    if not re.fullmatch(r"[0-9A-F]{16,20}", ecid):
        bot.reply_to(message, "❌ Invalid ECID format! Only Hex digit")
        return

    user = message.from_user
    user_id = user.id
    is_admin = (user.username or "").lower() == ADMIN_USERNAME.lower()

    now = time.time()

    # ---------- Лимит для обычных пользователей ----------
    if not is_admin:
        last = last_register_time.get(user_id, 0)
        remaining = COOLDOWN - (now - last)
        if remaining > 0:
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)
            bot.reply_to(
                message,
                f"⏳ You can register a new ECID in **{hours}h {minutes}m {seconds}s**",
                parse_mode="Markdown"
            )
            return

    # ---------- Регистрируем ECID ----------
    result = add_ecid(ecid, user_id, is_admin)
    status = result.get("status", "error")
    message_text = escape_markdown(result.get("message", "Unknown error"))

    if status == "success":
        bot.reply_to(message, f"✅ Registered {escape_markdown(ecid)} succesfully!", parse_mode="Markdown")
        if not is_admin:
            last_register_time[user_id] = now
    elif status == "exists":
        bot.reply_to(message, f"⚠️ ECID already Registered!", parse_mode="Markdown")
    elif status == "limit":
        # Получаем оставшееся время из ответа PHP, если сервер вернул его
        remaining_seconds = result.get("remaining", COOLDOWN)
        hours = int(remaining_seconds // 3600)
        minutes = int((remaining_seconds % 3600) // 60)
        seconds = int(remaining_seconds % 60)
        bot.reply_to(
            message,
            f"⏳ You can register a new ECID in **{hours}h {minutes}m {seconds}s**",
            parse_mode="Markdown"
        )
    elif status == "error":
        bot.reply_to(message, f"❌ Registration error: {message_text}", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Unknown status: {message_text}", parse_mode="Markdown")

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
        bot.reply_to(message, f"✅ Ecid {escape_markdown(ecid)} already registered")
    elif status == "error":
        bot.reply_to(message, f"❌ Server error: {message_text}")
    else:
        bot.reply_to(message, f"❌ Ecid `{escape_markdown(ecid)}` not registered")

# -------------------- DOWNLOAD --------------------
@bot.message_handler(commands=["download"])
def download(message):
    bot.reply_to(
        message,
        "📥 Download link:\n"
        "👉 App Will Released Soon 🕰️"
    )

bot.polling(none_stop=True)
