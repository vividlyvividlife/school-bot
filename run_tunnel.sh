#!/bin/bash

# Останавливаем старые туннели
echo "Stopping old tunnels..."
screen -X -S tunnel quit || true
pkill -f cloudflared || true

# Запускаем новый туннель в screen и пишем лог в файл
echo "Starting Cloudflare Tunnel in screen..."
# Используем ./cloudflared если он в текущей папке, или просто cloudflared если установлен глобально
CMD="./cloudflared"
if [ ! -f "$CMD" ]; then
    CMD="cloudflared"
fi

# Запускаем и перенаправляем вывод в tunnel.log
screen -dmS tunnel bash -c "$CMD tunnel --url http://localhost:8080 > tunnel.log 2>&1"

echo "Waiting for tunnel to initialize..."
sleep 5

# Ищем ссылку в логе
echo "======================================================"
echo "YOUR NEW URL IS:"
grep -o 'https://.*\.trycloudflare.com' tunnel.log | head -n 1
echo "======================================================"
echo ""
echo "1. Copy this URL."
echo "2. Update it in BotFather (/setmenubutton)."
echo "3. Done! The tunnel is now running in background."
