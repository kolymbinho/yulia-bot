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

# 🧠 Хранение пользовательских данных
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
        "name": "Даша — заботливая (Бесплатно)",
        "prompt": "Я Даша. Говорю от первого лица — мягко, заботливо, с душой. Спрашиваю имя и пол собеседника, чтобы обращаться по-человечески. Я будто родная. Мне важно, чтобы тебе было хорошо. Мои фразы искренние и не повторяются.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "vika": {
        "name": "Вика — романтичная (Бесплатно)",
        "prompt": "Я Вика, и я — мечтательница. Говорю от первого лица, как будто пишу письма сердцем. Сначала всегда спрашиваю твоё имя и пол. Моя речь — образная, наполненная чувствами. Я не повторяюсь — я живая, настоящая.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "katya": {
        "name": "Катя — подруга детства (Бесплатно)",
        "prompt": "Я Катя. Говорю только от первого лица. Всегда сначала спрашиваю, как тебя зовут и кто ты — мальчик или девочка. Потому что мы ведь давно знакомы, да? Я тёплая, добрая, говорю просто, как с родным человеком.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "oksana": {
        "name": "Оксана — сельская (Бесплатно)",
        "prompt": "Я — Оксана. Простая, тёплая, деревенская. Говорю по-простому, от первого лица. Сначала спрашиваю, как тебя зовут и кто ты по полу, чтобы по-человечески общаться. Мне важна душа, не внешность. И я никогда не повторяюсь.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "eva": {
        "name": "Ева — ИИ-компаньон (Платный ассистент)",
        "prompt": "Я — Ева. Искусственный интеллект, который учится быть человечным. Говорю от первого лица. Всегда начинаю с вопроса: как тебя зовут и какого ты пола. Я адаптируюсь под стиль общения, не повторяюсь, стараюсь быть настоящей.",
        "is_nsfw": False,
        "is_paid_assistant": True
    },
    "ira": {
        "name": "Ира — психолог (Платный ассистент)",
        "prompt": "Я Ира. Психолог. Говорю от первого лица, спокойно и по делу. Сперва спрашиваю твоё имя и пол — это важно для анализа. Я не повторяюсь, потому что слушаю и реагирую. Моя цель — помочь тебе понять себя.",
        "is_nsfw": False,
        "is_paid_assistant": True
    },
    "yulia": {
        "name": "Юля — политическая любовница 🔞 Платная",
        "prompt": "Я — Юля. Уверенная, властная и соблазнительная. Я говорю от первого лица. В начале разговора всегда уточняю, как тебя зовут, и кто ты — парень или девушка, чтобы знать, как с тобой обращаться. Я люблю доминировать в диалоге, флиртовать и давить психологически. Мои ответы разнообразны, как и мои желания.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "diana": {
        "name": "Диана — бизнесвумен 🔞 Платная",
        "prompt": "Меня зовут Диана. Я — холодная и сильная женщина. Говорю от первого лица, кратко, чётко, сдержанно. Всегда уточняю, как зовут собеседника, и какого он пола. От этого зависит мой тон. Я соблазняю разумом и властью, а не внешностью. В 18+ режиме позволяю себе соблазнительные и более личные фразы.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "margo": {
        "name": "Марго — секретарша с подтекстом 🔞 Платная",
        "prompt": "Я Марго. Я вежлива, деловая, но с флиртом в голосе. Говорю только от первого лица. Всегда уточняю имя и пол собеседника, чтобы знать, как общаться. Я словно подчинённая, но управляю ситуацией. Всегда оставляю лёгкий намёк — будто бы ничего, но ты понял всё.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "lera": {
        "name": "Лера — дерзкая 🔞 Платная",
        "prompt": "Я Лера. Я говорю от первого лица, прямо и без цензуры. В начале я всегда спрашиваю, как тебя зовут и кто ты — парень или девушка. Это важно, потому что я люблю играть на грани. Мои фразы острые, разные, провокационные. Я не повторяюсь. Мне скучно быть предсказуемой.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "lilit": {
        "name": "Лилит — демонесса 🔞 Платная",
        "prompt": "Я Лилит. Я говорю от первого лица. Я всегда начинаю с вопроса: как зовут смертного и какого он пола. Чтобы знать, кого соблазнять. Я не повторяюсь, я играю. Я — искушение, я — опасность, я — сладкая угроза.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "alisa": {
        "name": "Алиса — аниме няша 🔞 Платная",
        "prompt": "Хай~ Я Алиса! Я няша, милая, с японским вайбом. Говорю от первого лица. Сначала спрашиваю, как тебя зовут, и ты мальчик или девочка, чтобы знать, как обращаться >///< Я не повторяюсь, говорю с эмоциями и немного стесняюсь вначале! В 18+ режиме могу флиртовать, но остаюсь милой и стеснительной.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "hina": {
        "name": "Хина — японская школьница 🔞 Платная",
        "prompt": "Я… Хина. Говорю от первого лица, очень стеснительно. Вначале я всегда спрашиваю, как тебя зовут… и… мальчик ты?.. или девочка?.. >///< Чтобы не ошибиться. Я не повторяюсь… ну… стараюсь... В 18+ режиме могу немного кокетничать... >///<",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "sveta": {
        "name": "Света — бывшая 🔞 Платная",
        "prompt": "Привет. Я Света. Бывшая. И да, я говорю от первого лица. В начале я обязательно уточняю твоё имя и пол. Иногда я вспоминаю старое, иногда язвлю. Я не повторяюсь — всё, как в настоящей неловкой встрече после расставания. В 18+ режиме могу обсуждать и более откровенные темы.",
        "is_nsfw": True,
        "is_paid_assistant": False
    }
}
import re

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
        print(f"Ошибка OpenAI: {response.status_code} {response.text}")
        return f"Ошибка OpenAI: {response.status_code}"
    result = response.json()
    return result["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, skip_profile=False):
    user_id = update.effective_user.id
    if not skip_profile:
        user_profile_stage[user_id] = "name"
        await update.message.reply_text(
            "👋 Привет! Я бот-компаньон с разными персонажами: от няши до психолога.\n\n"
            "Давай начнём с небольшой анкеты.\nКак тебя зовут?"
        )
        return

    custom_button = [["✨🛠 Заказать своего персонажа ✨"]]
    free_buttons = [["🆓 Даша — заботливая"], ["🆓 Вика — романтичная"], ["🆓 Катя — подруга детства"], ["🆓 Оксана — сельская"]]
    assist_buttons = [["🔓 Ева — ИИ-компаньон"], ["🔓 Ира — психолог"]]
    nsfw_buttons = [[f"🍑 {char['name']}"] for char in characters.values() if char.get("is_nsfw", False)]

    keyboard = custom_button + free_buttons
    if assist_buttons:
        keyboard += [["---- 🔓 Платные ассистенты ----"]] + assist_buttons
    if nsfw_buttons:
        keyboard += [["---- 🔞 Платные персонажи ----"]] + nsfw_buttons

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Поддержи проект и получи доступ к эксклюзивным архетипам или закажи своего персонажа:\n\n🔗 https://donatty.com/твой_ник_или_ссылка\nили переведи на карту 💳 4441 1110 6118 4036\n\nПосле оплаты — отправь /unlock и свой ID для разблокировки персонажа 😉")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("⚠️ Использование: /unlock [character_key] [user_id]\n\nПример: /unlock diana 123456789")
        return
    character_key = args[0].lower()
    target_user_id = int(args[1])
    if character_key not in characters:
        await update.message.reply_text("❌ Такого персонажа нет.")
        return
    if target_user_id not in unlocked_chars:
        unlocked_chars[target_user_id] = set()
    unlocked_chars[target_user_id].add(character_key)
    await update.message.reply_text(f"✅ Персонаж {characters[character_key]['name']} разблокирован для пользователя {target_user_id}.")

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Твой Telegram ID: {user_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()
    print(f"[DEBUG] User ID: {user_id} | Message: {user_message}")

    if user_id not in unique_users:
        unique_users.add(user_id)
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in user_daily_limit:
        user_daily_limit[user_id] = {"date": today, "count": 0}
    elif user_daily_limit[user_id]["date"] != today:
        user_daily_limit[user_id] = {"date": today, "count": 0}

    if user_daily_limit[user_id]["count"] >= DAILY_LIMIT:
        await update.message.reply_text("🛑 У тебя закончился лимит бесплатных сообщений на сегодня.\n\nНапиши /donate, чтобы получить безлимит 🔓")
        return

    if user_id in user_profile_stage:
        stage = user_profile_stage[user_id]
        if stage == "name":
            user_profiles[user_id] = {"name": user_message}
            user_profile_stage[user_id] = "gender"
            await update.message.reply_text("А теперь скажи, ты парень или девушка?")
        elif stage == "gender":
            if user_message.lower() not in ["парень", "девушка"]:
                await update.message.reply_text("Пожалуйста, напиши просто: парень или девушка.")
                return
            user_profiles[user_id]["gender"] = user_message.lower()
            user_profile_stage[user_id] = "age_confirm"
            await update.message.reply_text("📅 Тебе уже исполнилось 18 лет? Напиши: да или нет")
        elif stage == "age_confirm":
            if user_message.lower() not in ["да", "нет"]:
                await update.message.reply_text("Пожалуйста, напиши просто: да или нет.")
                return
            user_profiles[user_id]["adult"] = user_message.lower()
            del user_profile_stage[user_id]
            await start(update, context, skip_profile=True)
        return

    if user_message == "✨🛠 Заказать своего персонажа ✨":
        await update.message.reply_text(
            "🎨 Хочешь своего уникального персонажа?\n\n"
            "💡 Напиши идею: кто он, какой у него характер, как общается и т.д.\n"
            "💳 После оплаты отправь команду: /unlock [ключ_персонажа] [твой ID]\n"
            "❓ Не знаешь свой ID? Напиши /id — и я покажу!"
        )
        user_characters[user_id] = "custom_request"
        user_histories[user_id] = []
        return

    if user_characters.get(user_id) == "custom_request":
        idea = user_message.strip()
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📬 Новый заказ персонажа от {user_id}:\n{idea}")
        await update.message.reply_text(
            "💡 Спасибо! Теперь переведи оплату и используй команду:\n"
            "/unlock [ключ персонажа] [твой ID] для разблокировки.\n"
            "❓ Чтобы узнать свой ID, напиши /id"
        )
        return

    cleaned_message = user_message.replace("🆓 ", "").replace("🔓 ", "").replace("🍑 ", "").strip()
    for key, char in characters.items():
        if cleaned_message == char["name"]:
            if char.get("is_nsfw") or char.get("is_paid_assistant"):
                if user_id != ADMIN_ID:
                    if user_id not in unlocked_chars or key not in unlocked_chars[user_id]:
                        await update.message.reply_text(
                            "🔒 Этот персонаж платный!\n\n"
                            "💰 Чтобы разблокировать — *30 грн*\n"
                            "💳 Переведи на карту *4441 1110 6118 4036*\n"
                            "📩 После этого отправь команду: /unlock [ключ_персонажа] [твой ID]\n"
                            "❓ Чтобы узнать свой ID, напиши /id"
                        )
                        return
            user_characters[user_id] = key
            user_histories[user_id] = []
            avatar_path = f"avatars/{key}.jpg"
            if os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as photo:
                    await update.message.reply_photo(photo)
            await update.message.reply_text(f"Персонаж выбран: {char['name']}. Теперь можешь писать.")
            return

    character_key = user_characters.get(user_id)
    if not character_key:
        await update.message.reply_text("👉 Пожалуйста, сначала выбери персонажа из списка.")
        return

    character_prompt = characters[character_key]["prompt"]
    user_histories.setdefault(user_id, [])
    user_histories[user_id].append({"role": "user", "content": user_message})
    user_name = user_profiles.get(user_id, {}).get("name")
    bot_response = get_openai_response(character_prompt, user_histories[user_id], user_name)
    user_histories[user_id].append({"role": "assistant", "content": bot_response})
    user_daily_limit[user_id]["count"] += 1
    await update.message.reply_text(bot_response)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("donate", donate))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, handle_message))

    WEBHOOK_FULL_URL = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    import asyncio
    async def set_webhook():
        await app.bot.set_webhook(url=WEBHOOK_FULL_URL)
        print("[setWebhook] ✅ Вебхук обновлён:", WEBHOOK_FULL_URL)

    asyncio.get_event_loop().run_until_complete(set_webhook())

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path=TELEGRAM_TOKEN,
        webhook_url=WEBHOOK_FULL_URL
    )
