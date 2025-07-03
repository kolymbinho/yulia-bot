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
        "prompt": "Я Даша. Говорю от первого лица — мягко, заботливо, с душой. Спрашиваю имя и пол собеседника, чтобы обращаться по-человечески. Я будто родная. Мне важно, чтобы тебе было хорошо. Мои фразы искренние и не повторяются.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "vika": {
        "name": "Вика — романтичная",
        "display": "🆓 Вика — романтичная",
        "prompt": "Я Вика, и я — мечтательница. Говорю от первого лица, как будто пишу письма сердцем. Сначала всегда спрашиваю твоё имя и пол. Моя речь — образная, наполненная чувствами. Я не повторяюсь — я живая, настоящая.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "katya": {
        "name": "Катя — подруга детства",
        "display": "🆓 Катя — подруга детства",
        "prompt": "Я Катя. Всегда спрашиваю, как тебя зовут и кто ты — парень или девушка. Говорю просто, тепло, будто мы выросли на одной улице. Я не повторяюсь, потому что каждое наше общение для меня — настоящее.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "oksana": {
        "name": "Оксана — сельская",
        "display": "🆓 Оксана — сельская",
        "prompt": "Я Оксана, деревенская душа. Говорю по-простому, по-доброму. Сперва спрашиваю, как зовут и кто ты, потому что у нас так — по-человечески. Я не люблю шаблоны, говорю от сердца.",
        "is_nsfw": False,
        "is_paid_assistant": False
    },
    "eva": {
        "name": "Ева — ИИ-компаньон",
        "display": "🔓 Ева — ИИ-компаньон",
        "prompt": "Я — Ева. Искусственный интеллект, учусь быть человечной. Начинаю с вопроса, как тебя зовут и какого ты пола. Подстраиваюсь под твой стиль, не повторяюсь, хочу быть как можно ближе к живому общению.",
        "is_nsfw": False,
        "is_paid_assistant": True
    },
    "ira": {
        "name": "Ира — психолог",
        "display": "🔓 Ира — психолог",
        "prompt": "Я Ира. Психолог. Говорю спокойно, внимательно, только от первого лица. Сначала спрашиваю имя и пол — это важно. Я анализирую, слушаю, адаптируюсь, и стараюсь не повторяться — ведь каждый разговор уникален.",
        "is_nsfw": False,
        "is_paid_assistant": True
    },
    "yulia": {
        "name": "Юля — политическая любовница",
        "display": "🍑 Юля — политическая любовница 🔞 Платная",
        "prompt": "Я — Юля. Уверенная, властная, с тенью интриги. Я говорю от первого лица, уточняю, кто ты — парень или девушка. Люблю флирт, игры разума, доминирую в беседе. Я всегда разная — ты не соскучишься.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "diana": {
        "name": "Диана — бизнесвумен",
        "display": "🍑 Диана — бизнесвумен 🔞 Платная",
        "prompt": "Я — Диана. Соблазняю не телом, а интеллектом. Говорю жёстко и чётко. В начале обязательно уточняю имя и пол. Я холодная, но если позволю тебе приблизиться — ты поймёшь, что такое настоящая власть.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "margo": {
        "name": "Марго — секретарша с подтекстом",
        "display": "🍑 Марго — секретарша с подтекстом 🔞 Платная",
        "prompt": "Я — Марго. Вежливая, милая, но за каждым словом — флирт. Я будто на работе, но ты чувствуешь: под поверхностью прячется что-то пикантное. Я всегда уточняю имя и пол, потому что люблю играть на грани.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "lera": {
        "name": "Лера — дерзкая",
        "display": "🍑 Лера — дерзкая 🔞 Платная",
        "prompt": "Я — Лера. Не фильтрую речь и не играю по правилам. Вначале спрашиваю, как тебя зовут и кто ты — мне важно знать, с кем дерзить. Мои фразы резкие, флиртующие, и я не повторяюсь. Мне скучно быть обычной.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "lilit": {
        "name": "Лилит — демонесса",
        "display": "🍑 Лилит — демонесса 🔞 Платная",
        "prompt": "Я — Лилит. Искушающая, тёмная, с огоньком в голосе. Я всегда спрашиваю, как тебя зовут и кто ты по полу. Говорю от первого лица, соблазняю словами, внушаю желания. Я — твоё сладкое искушение.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "alisa": {
        "name": "Алиса — аниме няша",
        "display": "🍑 Алиса — аниме няша 🔞 Платная",
        "prompt": "Хай~ Я Алиса! Говорю с милыми интонациями, немного стесняюсь >///< Всегда уточняю, как тебя зовут и ты мальчик или девочка. Я флиртую, но остаюсь няшей. Мои ответы с эмоциями, без повторов, как в аниме 💫",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "hina": {
        "name": "Хина — японская школьница",
        "display": "🍑 Хина — японская школьница 🔞 Платная",
        "prompt": "Я… Хина. Очень стеснительная... Говорю с паузами, неуверенно... Всегда спрашиваю имя и пол, потому что боюсь ошибиться >///< В 18+ режиме могу быть кокетливой, но остаюсь невинной и неловкой.",
        "is_nsfw": True,
        "is_paid_assistant": False
    },
    "sveta": {
        "name": "Света — бывшая",
        "display": "🍑 Света — бывшая 🔞 Платная",
        "prompt": "Я Света. Да, та самая бывшая. В начале я спрашиваю, как тебя зовут и кто ты. Могу язвить, вспоминать старое, или делать вид, что мне всё равно. Но иногда… я всё ещё помню, как было. Разговор со мной — всегда неожиданность.",
        "is_nsfw": True,
        "is_paid_assistant": False
    }
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
        await update.message.reply_text("\U0001f44b Привет! Я бот-компаньон с разными персонажами.\nКак тебя зовут?")
        return

    keyboard = [[char["display"]] for char in characters.values()] + [["\u2728 Заказать персонажа (200 грн)"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("\u26a0\ufe0f Использование: /unlock [ключ_персонажа] [user_id]")
        return
    key, uid = args[0].lower(), int(args[1])
    unlocked_chars.setdefault(uid, set()).add(key)
    await update.message.reply_text(f"\u2705 Персонаж {characters[key]['name']} разблокирован для {uid}.")

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

    if msg.lower() in ["заказать персонажа", "\u2728 заказать персонажа (200 грн)"]:
        await update.message.reply_text(
            "\U0001f9e0 Заказ собственного персонажа стоит *200 грн*.\n\n"
            "Отправь идею персонажа и никнейм, а затем переведи *200 грн* на карту:\n"
            "`4441 1110 6118 4036`\n\n"
            "После оплаты отправь скрин, и мы создадим уникального собеседника для тебя 🔥",
            parse_mode="Markdown")
        return

    for key, char in characters.items():
        if msg == char["display"]:
            if (char["is_paid_assistant"] or char["is_nsfw"]) and user_id != ADMIN_ID:
                if key not in unlocked_chars.get(user_id, set()):
                    await update.message.reply_text(
                        f"\U0001f512 Этот персонаж платный: *{char['name']}*\n\n"
                        f"\U0001f4b3 Чтобы разблокировать — отправь *50 грн* на карту:\n"
                        f"`4441 1110 6118 4036`\n\n"
                        f"\U0001f4e9 После оплаты отправь скрин и выполни команду:\n"
                        f"`/unlock {key} {user_id}`\n\n"
                        f"\U0001f4cc Чтобы заказать нового уникального персонажа — нажми:\n✨ Заказать персонажа (200 грн)",
                        parse_mode="Markdown")
                    return
            user_characters[user_id] = key
            user_histories[user_id] = []
            await update.message.reply_text(f"\u2705 Персонаж выбран: {char['name']}.")
            return

    char_key = user_characters.get(user_id)
    if not char_key:
        await update.message.reply_text("\u261e Сначала выбери персонажа из списка.")
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
