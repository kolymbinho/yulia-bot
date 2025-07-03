# ✅ ОБНОВЛЕННЫЙ main.py с разделением `name` и `display`
import re
import os
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters as tg_filters
from datetime import datetime

# Загрузка .env
load_dotenv()

user_characters = {}
user_nsfw = {}
user_histories = {}
user_profiles = {}
user_profile_stage = {}
user_daily_limit = {}
unlocked_chars = {}
unique_users = set()
DAILY_LIMIT = 15
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

characters = {
    "dasha": {
        "name": "Даша — заботливая",
        "display": "🆓 Даша — заботливая",
        "prompt": "Я Даша. Говорю от первого лица — мягко, заботливо...",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "katya": {
        "name": "Катя — подруга детства",
        "display": "🆓 Катя — подруга детства",
        "prompt": "Я Катя. Говорю только от первого лица...",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "lilit": {
        "name": "Лилит — демонесса",
        "display": "🍑 Лилит — демонесса 🔞 Платная",
        "prompt": "Я Лилит. Я говорю от первого лица...",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    # ➕ Добавь остальных по той же схеме (display отдельно)
}

# Очистка prompt'ов от дублирующихся фраз
for char in characters.values():
    char["prompt"] = re.sub(
        r"(всегда\\s)?(спрашиваю|уточняю|начинаю с вопроса)[^\\.!?]{0,100}(имя|зовут|пол)[^\\.!?]{0,100}[\\.!?]",
        "",
        char["prompt"],
        flags=re.IGNORECASE
    ).strip()

def get_openai_response(character_prompt, history, user_name=None):
    if user_name:
        character_prompt = f"Обращайся к собеседнику по имени — {user_name}. " + character_prompt
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [{"role": "system", "content": character_prompt}] + history
    data = {"model": "gpt-4o", "messages": messages}
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code != 200:
        return f"Ошибка OpenAI: {response.status_code}"
    return response.json()["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, skip_profile=False):
    user_id = update.effective_user.id
    if not skip_profile:
        user_profile_stage[user_id] = "name"
        await update.message.reply_text(
            "👋 Привет! Я бот-компаньон с разными персонажами.\nКак тебя зовут?")
        return

    keyboard = [[char["display"]] for char in characters.values()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("⚠️ Использование: /unlock [ключ_персонажа] [user_id]")
        return
    key, uid = args[0].lower(), int(args[1])
    unlocked_chars.setdefault(uid, set()).add(key)
    await update.message.reply_text(f"✅ Персонаж {characters[key]['name']} разблокирован для {uid}.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()

    if user_id not in unique_users:
        unique_users.add(user_id)
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

    if user_id not in user_daily_limit:
        user_daily_limit[user_id] = {"date": datetime.now().strftime("%Y-%m-%d"), "count": 0}

    if user_profile_stage.get(user_id):
        stage = user_profile_stage[user_id]
        if stage == "name":
            user_profiles[user_id] = {"name": msg}
            user_profile_stage[user_id] = "gender"
            await update.message.reply_text("Теперь скажи, ты парень или девушка?")
        elif stage == "gender":
            if msg.lower() not in ["парень", "девушка"]:
                await update.message.reply_text("Напиши просто: парень или девушка.")
                return
            user_profiles[user_id]["gender"] = msg
            user_profile_stage[user_id] = "age"
            await update.message.reply_text("Тебе уже исполнилось 18 лет? Напиши: да или нет")
        elif stage == "age":
            if msg.lower() not in ["да", "нет"]:
                await update.message.reply_text("Напиши просто: да или нет.")
                return
            user_profiles[user_id]["adult"] = msg
            del user_profile_stage[user_id]
            await start(update, context, skip_profile=True)
        return

    # 👉 Заказ персонажа (если хочешь)
    if msg.startswith("✨"):
        await update.message.reply_text("🎨 Напиши, какого персонажа хочешь.")
        return

    for key, char in characters.items():
        if msg == char["display"]:
            if (char["is_paid_assistant"] or char["is_nsfw"]) and user_id != ADMIN_ID:
                if key not in unlocked_chars.get(user_id, set()):
                    await update.message.reply_text("🔒 Этот персонаж платный. Чтобы разблокировать — напиши /unlock [ключ] [id]")
                    return
            user_characters[user_id] = key
            user_histories[user_id] = []
            await update.message.reply_text(f"Персонаж выбран: {char['name']}. Теперь можешь писать.")
            return

    char_key = user_characters.get(user_id)
    if not char_key:
        await update.message.reply_text("👉 Сначала выбери персонажа из списка.")
        return

    prompt = characters[char_key]["prompt"]
    user_histories.setdefault(user_id, []).append({"role": "user", "content": msg})
    name = user_profiles.get(user_id, {}).get("name")
    reply = get_openai_response(prompt, user_histories[user_id], name)
    user_histories[user_id].append({"role": "assistant", "content": reply})
    user_daily_limit[user_id]["count"] += 1
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, handle_message))

    WEBHOOK_FULL_URL = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    import asyncio
    asyncio.get_event_loop().run_until_complete(app.bot.set_webhook(url=WEBHOOK_FULL_URL))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path=TELEGRAM_TOKEN,
        webhook_url=WEBHOOK_FULL_URL
    )
