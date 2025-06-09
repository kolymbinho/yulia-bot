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



# Для хранения выбранных персонажей
user_characters = {}

# Для хранения 18+ режима
user_nsfw = {}

# Для хранения истории сообщений
user_histories = {}

# GPT
def get_openai_response(character_prompt, history):
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

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Генерация кнопок

    # Бесплатные
    free_buttons = [[char["name"]] for char in characters.values() if not char.get("is_nsfw", False) and not char.get("is_paid_assistant", False)]

    # Платные ассистенты
    assist_buttons = [[char["name"]] for char in characters.values() if char.get("is_paid_assistant", False)]

    # Платные 🔞
    nsfw_buttons = [[char["name"]] for char in characters.values() if char.get("is_nsfw", False)]

    # Собираем итоговую клавиатуру
    keyboard = free_buttons

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

    # Если выбрал персонажа
    for key, char in characters.items():
        if user_message == char["name"]:
            user_characters[user_id] = key
            user_histories[user_id] = []  # Сбросить историю при выборе нового персонажа

            # Путь к аватарке
            avatar_path = f"avatars/{key}.jpg"

            # Проверяем если файл существует — отправляем
            if os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as photo:
                    await update.message.reply_photo(photo)

            # Текст
            await update.message.reply_text(f"Персонаж выбран: {char['name']}. Теперь можешь писать.")
            return

    # Если персонаж не выбран — Юля по умолчанию
    character_key = user_characters.get(user_id, "yulia")
    character_prompt = characters[character_key]["prompt"]

    # Инициализация истории, если нет
    user_histories.setdefault(user_id, [])

    # Добавляем сообщение пользователя в историю
    user_histories[user_id].append({"role": "user", "content": user_message})

    print(f"Получено сообщение: {user_message}")  

    # Получаем ответ GPT
    bot_response = get_openai_response(character_prompt, user_histories[user_id])

    # Добавляем ответ бота в историю
    user_histories[user_id].append({"role": "assistant", "content": bot_response})

    await update.message.reply_text(bot_response)



# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен! Используем Webhook:", WEBHOOK_URL)

# Автоматический setWebhook
setwebhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}/{TELEGRAM_TOKEN}"

try:
    r = requests.get(setwebhook_url)
    if r.status_code == 200:
        print(f"[setWebhook] ✅ Webhook обновлён: {WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    else:
        print(f"[setWebhook] ❌ Ошибка {r.status_code}: {r.text}")
except Exception as e:
    print(f"[setWebhook] ❌ Исключение: {e}")

# Запуск бота
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.getenv("PORT", 10000)),
    url_path=TELEGRAM_TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
)

