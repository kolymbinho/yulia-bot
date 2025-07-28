#!/bin/bash

# Получаем токен и вебхук из переменных среды (Render Environment)
BOT_TOKEN=$TELEGRAM_TOKEN
WEBHOOK_URL=$RENDER_URL

# Устанавливаем webhook
curl -s -X POST https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$WEBHOOK_URL

echo "Webhook обновлён!"
