#!/bin/bash

# Включаем логирование
exec > >(tee -a /botSchool/deploy.log) 2>&1
echo "=== Deploy started at $(date) ==="

# Переходим в директорию проекта
cd /botSchool || { echo "Failed to change directory to /botSchool"; exit 1; }
echo "Changed to directory: $(pwd)"

# Останавливаем текущую screen сессию если она есть
echo "Stopping existing screen session..."
screen -X -S school_bot quit || true
# Принудительно убиваем старые процессы, если они зависли
pkill -f "python bot_with_webapp.py" || true
pkill -f "python bot.py" || true

# Сохраняем текущие настройки если нужно
if [ -f .env ]; then
    cp .env .env.backup
    echo "Backed up .env file"
fi

# Очищаем директорию от неотслеживаемых файлов
echo "Cleaning repository..."
git clean -df
git reset --hard

# Получаем последние изменения
echo "Fetching latest changes..."
git fetch origin main
git reset --hard origin/main

# Восстанавливаем .env если он был
if [ -f .env.backup ]; then
    mv .env.backup .env
    echo "Restored .env file"
fi

# Активируем venv и обновляем зависимости
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created new virtual environment"
fi

echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Проверяем базу данных
if [ ! -f "school_bot.db" ]; then
    echo "Database not found, will be created on first run"
fi

# Запускаем бота в screen
echo "Starting bot in screen session..."
screen -dmS school_bot bash -c "source venv/bin/activate && python bot_with_webapp.py"

# Проверяем, запустился ли screen
sleep 2
if screen -ls | grep -q "school_bot"; then
    echo "✅ Bot successfully started in screen session 'school_bot'"
    echo "To view logs: screen -r school_bot"
    echo "To detach: Ctrl+A, then D"
else
    echo "❌ Failed to start bot in screen session!"
    exit 1
fi

# Показываем статус
echo ""
echo "=== Deployment Status ==="
echo "Screen sessions:"
screen -ls
echo ""
echo "Recent logs:"
tail -n 20 bot.log 2>/dev/null || echo "No bot.log found yet"

echo ""
echo "=== Deploy finished at $(date) ==="
