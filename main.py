import os
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Загружаем переменные из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL").strip()

# Твой Telegram ID для уведомлений
ADMIN_ID = 397749139  # ← сюда свой ID из лога

# ХАРАКТЕРЫ
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
        r"(всегда\s)?(спрашиваю|уточняю|начинаю с вопроса)[^\.!?]{0,100}(имя|зовут|пол)[^\.!?]{0,100}[\.!?]",
        "",
        char["prompt"],
        flags=re.IGNORECASE
    ).strip()
# 🧠 Хранение пользовательских данных

# Выбранный персонаж
user_characters = {}

# Активирован ли режим 18+
user_nsfw = {}

# История сообщений
user_histories = {}

# Профиль пользователя: имя, пол, возраст
user_profiles = {}  # user_id → {"name": ..., "gender": ..., "age": ...}

# Этап анкеты, на котором находится пользователь
user_profile_stage = {}  # user_id → "name" | "gender" | "age"

from datetime import datetime

# Ограничение сообщений в день
user_daily_limit = {}  # user_id → {"date": "2025-06-09", "count": 7}
DAILY_LIMIT = 15

# GPT
def get_openai_response(character_prompt, history, user_name=None):
    if user_name:
        character_prompt = f"Обращайся к собеседнику по имени — {user_name}. " + character_prompt
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [{"role": "system", "content": character_prompt}] + history

    data = {
        "model": "gpt-4o",
        "messages": messages
    }

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

    # Показ клавиатуры персонажей после анкеты
    custom_button = [["✨🛠 Заказать своего персонажа ✨"]]
    free_buttons = [[char["name"]] for char in characters.values() if not char.get("is_nsfw", False) and not char.get("is_paid_assistant", False)]
    assist_buttons = [[char["name"]] for char in characters.values() if char.get("is_paid_assistant", False)]
    nsfw_buttons = [[char["name"]] for char in characters.values() if char.get("is_nsfw", False)]

    keyboard = custom_button + free_buttons
    if assist_buttons:
        keyboard += [["---- Платные ассистенты ----"]] + assist_buttons
    if nsfw_buttons:
        keyboard += [["---- 🔞 Платные персонажи ----"]] + nsfw_buttons

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)




# Сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    print(f"[DEBUG] User ID: {user_id} | Message: {user_message}")

    # 🔒 Проверка лимита сообщений в день
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in user_daily_limit:
        user_daily_limit[user_id] = {"date": today, "count": 0}
    elif user_daily_limit[user_id]["date"] != today:
        user_daily_limit[user_id] = {"date": today, "count": 0}

    if user_daily_limit[user_id]["count"] >= DAILY_LIMIT:
        await update.message.reply_text("🛑 У тебя закончился лимит бесплатных сообщений на сегодня.\n\nНапиши /donate, чтобы получить безлимит 🔓")
        return

    # ⛓ Этап анкеты
    if user_id in user_profile_stage:
        stage = user_profile_stage[user_id]

        if stage == "name":
            user_profiles[user_id] = {"name": user_message}
            user_profile_stage[user_id] = "gender"
            await update.message.reply_text("😊 Приятно! А теперь скажи, ты парень или девушка?")
            return

        elif stage == "gender":
            user_profiles[user_id]["gender"] = user_message
            user_profile_stage[user_id] = "age"
            await update.message.reply_text("📅 Отлично! И сколько тебе лет?")
            return

        elif stage == "age":
            user_profiles[user_id]["age"] = user_message
            del user_profile_stage[user_id]  # анкета завершена

            await update.message.reply_text(
                f"✨ Спасибо, {user_profiles[user_id]['name']}!\n"
                "Теперь выбери персонажа, с кем хочешь пообщаться 👇"
            )

            await start(update, context, skip_profile=True)
            return

    # Обработка кнопки "✨🛠 Заказать своего персонажа ✨"
    if user_message == "✨🛠 Заказать своего персонажа ✨":
        user_characters[user_id] = "custom_request"  # Включаем спец-режим
        user_histories[user_id] = []  # Очищаем историю
        await update.message.reply_text(
            "🎨 Напиши, какого персонажа ты хочешь.\n\n"
            "Это может быть кто угодно — философ, воин, диктатор, соблазнитель, аниме-девочка, демон, бог, бывшая, кто угодно 😈\n\n"
            "💬 Пример: «Хочу девушку-киборга, которая говорит как ведьма из Skyrim»"
        )
        return

    # Пользователь описал идею кастомного персонажа
    if user_characters.get(user_id) == "custom_request":
        idea = user_message.strip()
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📬 Новый заказ персонажа от пользователя {user_id}:\n{idea}"
        )
        await update.message.reply_text(
            f"💡 Круто! Ты хочешь: «{idea}»\n\n"
            f"Чтобы создать такого персонажа, нужна оплата 💳\n"
            f"👉 Напиши /donate — и я покажу, как поддержать проект и получить персонального бота."
        )
        return

    # Если выбрал персонажа
    for key, char in characters.items():
        if user_message == char["name"]:
            if char.get("is_nsfw", False) or char.get("is_paid_assistant", False):
                if user_id != ADMIN_ID:
                    if user_id not in unlocked_chars or key not in unlocked_chars[user_id]:
                        await update.message.reply_text("🔒 Этот персонаж платный. Напиши /donate, чтобы получить доступ.")
                        return

            user_characters[user_id] = key
            user_histories[user_id] = []  # Сброс истории

            avatar_path = f"avatars/{key}.jpg"
            if os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as photo:
                    await update.message.reply_photo(photo)

            await update.message.reply_text(f"Персонаж выбран: {char['name']}. Теперь можешь писать.")
            return

    # Получаем текущего персонажа (по умолчанию Юля)
    character_key = user_characters.get(user_id, "yulia")
    character_prompt = characters[character_key]["prompt"]

    user_histories.setdefault(user_id, [])
    user_histories[user_id].append({"role": "user", "content": user_message})

    user_name = user_profiles.get(user_id, {}).get("name")
    bot_response = get_openai_response(character_prompt, user_histories[user_id], user_name)
    user_histories[user_id].append({"role": "assistant", "content": bot_response})

    # ✅ Увеличиваем счётчик сообщений
    user_daily_limit[user_id]["count"] += 1

    await update.message.reply_text(bot_response)


# Команда /donate — отправляет пользователю инфу о поддержке
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Поддержи проект и получи доступ к эксклюзивным архетипам или закажи своего персонажа:\n\n"
        "🔗 https://donatty.com/твой_ник_или_ссылка\n"
        "или переведи на карту 💳 5375 41XX XXXX XXXX\n\n"
        "После оплаты — напиши мне, и я всё активирую вручную 😉"
    )


# ⛓ Хранилище разблокированных персонажей (user_id → set(character_keys))
unlocked_chars = {}

# Команда для ручной разблокировки платного персонажа по ID
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Эта команда доступна только админу.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("⚠️ Использование: /разблокировать [ключ_персонажа] [user_id]\n\nПример: /разблокировать diana 8155706934")
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


import asyncio  # обязательно ВВЕРХУ!

# Запуск
if __name__ == "__main__":
    import asyncio

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("donate", donate))
    app.add_handler(CommandHandler("unlock", unlock))

    # Сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook
    WEBHOOK_FULL_URL = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    print("Бот запущен! Используем Webhook:", WEBHOOK_FULL_URL)

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
