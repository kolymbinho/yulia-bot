#!/bin/bash

# Токен твоего бота
BOT_TOKEN="7307123618:AAEMGpYkprJoc0Om7T4T33s8PFlbC-0xHcU"

# Webhook URL
WEBHOOK_URL="https://yulia-bot-iplb.onrender.com/$BOT_TOKEN"

# Установка Webhook
curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" -d "url=$WEBHOOK_URL"

echo "✅ Webhook обновлён на: $WEBHOOK_URL"
