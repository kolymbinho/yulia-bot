import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Загружаем переменные окружения
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Получаем ответ от OpenAI
def get_openai_response(prompt):
    api_key = (OPENAI_API_KEY or "").strip()

    if not api_key:
        print("OpenAI API key is not set")
        return "Ошибка: API KEY не задан."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o",
        "messages": [
            { "role": "user", "content": prompt }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        print(f"Ошибка OpenAI: {response.status_code} {response.text}")
        return f"Ошибка OpenAI: {response.status_code}"

    result = response.json()
    print(f"Ответ OpenAI: {result}")

    return result["choices"][0]["message"]["content"]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Юля-Бот (GPT-4o). Напиши мне что-нибудь!")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    bot_response = get_openai_response(user_message)
    await update.message.reply_text(bot_response)

# Запуск бота с Webhook
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен на Webhook!")
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )
