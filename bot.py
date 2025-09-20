import time
from datetime import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from openai import OpenAI

# ==========================
# Logging sozlamalari
# ==========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==========================
# API va Token
# ==========================
OPENAI_API_KEY = "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"
TELEGRAM_TOKEN = "8209823575:AAEOvRBIZTbj9aM04cEIysnuOlYzXh_yan8"

client = OpenAI(api_key=OPENAI_API_KEY)
user_sessions = {}

# ==========================
# Inline tugmalar yaratish
# ==========================
def get_keyboard():
    buttons = [
        [InlineKeyboardButton("Salom 👋", callback_data="salom")],
        [InlineKeyboardButton("Hazil 😂", callback_data="hazil")],
        [InlineKeyboardButton("So‘nggi 10 xabar 📜", callback_data="session")]
    ]
    return InlineKeyboardMarkup(buttons)

# ==========================
# /start komandasi
# ==========================
def start(update, context):
    update.message.reply_text(
        "Salom! Men aqlli botman. Siz menga savol yozsangiz, men javob beraman.\n"
        "Yordam uchun /help yozing.",
        reply_markup=get_keyboard()
    )

# ==========================
# /help komandasi
# ==========================
def help_command(update, context):
    update.message.reply_text(
        "Bu bot OpenAI GPT modeliga ulanadi.\n"
        "- Siz xabar yozasiz → bot javob beradi\n"
        "- Inline tugmalar orqali ham javob olishingiz mumkin\n"
        "- /start → boshlash\n"
        "- /help → yordam",
        reply_markup=get_keyboard()
    )

# ==========================
# Inline tugma bosilganda
# ==========================
def button(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == "salom":
        query.edit_message_text("Salom! Siz bilan gaplashishdan xursandman 😄")
    elif query.data == "hazil":
        query.edit_message_text("Ha-ha, hazilni tushundim 😆")
    elif query.data == "session":
        session_text = "\n".join(user_sessions.get(user_id, [])) or "Hech qanday xabar yo‘q."
        query.edit_message_text(f"So‘nggi xabarlaringiz:\n{session_text}")

# ==========================
# Foydalanuvchi yozgan xabarni OpenAI orqali javoblash
# ==========================
def chat(update, context):
    user_id = update.message.from_user.id
    user_message = update.message.text.strip()

    if len(user_message) == 0:
        update.message.reply_text("Xabar bo‘sh bo‘lishi mumkin emas.")
        return

    # Session saqlash (so‘nggi 10 xabar, vaqt bilan)
    timestamp = datetime.now().strftime("%H:%M:%S")
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    user_sessions[user_id].append(f"[{timestamp}] {user_message}")
    if len(user_sessions[user_id]) > 10:
        user_sessions[user_id].pop(0)

    try:
        combined_message = "\n".join(user_sessions[user_id])
        if len(combined_message) > 2000:
            combined_message = combined_message[-2000:]

        response = client.responses.create(
            model="gpt-4o-mini",
            input=combined_message
        )
        reply = response.output[0].content[0].text
        update.message.reply_text(reply)
    except Exception as e:
        update.message.reply_text(f"Xatolik yuz berdi: {e}\nIltimos internetga ulanganingizni tekshiring.")

# ==========================
# Botni ishga tushirish (auto-restart)
# ==========================
def run_bot():
    while True:
        try:
            updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
            dispatcher = updater.dispatcher

            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help_command))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))
            dispatcher.add_handler(CallbackQueryHandler(button))

            logging.info("Bot ishga tushdi...")
            updater.start_polling()
            updater.idle()
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}. Bot 5 soniyadan keyin qayta ishga tushadi...")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
