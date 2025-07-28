#!/bin/bash

# Твой токен сюда (без кавычек)
BOT_TOKEN=7307123618:AAHJz5fRZRIu9rnEsdSPeaM24Fnj1S-EKiU

# Твой вебхук (из ENV)
WEBHOOK_URL="https://yulia-bot-iplb.onrender.com"

# Отправляем запрос на установку webhook
curl -s -X POST https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$WEBHOOK_URL/$BOT_TOKEN

echo "Webhook обновлён!"
