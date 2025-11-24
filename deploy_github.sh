#!/bin/bash
# Скрипт для деплоя Mini App на GitHub Pages

echo "========================================"
echo "  School Bot - GitHub Pages Deploy"
echo "========================================"
echo ""

# Проверка наличия Git
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git не установлен!"
    echo "Установите Git: https://git-scm.com"
    exit 1
fi

echo "[1/5] Переход в директорию webapp..."
cd webapp

# Проверка наличия .git
if [ ! -d ".git" ]; then
    echo ""
    echo "[2/5] Инициализация Git репозитория..."
    git init
    
    echo ""
    echo "[!] Введите URL вашего GitHub репозитория:"
    echo "Формат: https://github.com/USERNAME/REPO_NAME.git"
    read -p "URL: " REPO_URL
    
    git remote add origin "$REPO_URL"
else
    echo "[2/5] Git репозиторий уже инициализирован"
fi

echo ""
echo "[3/5] Добавление файлов..."
git add .

echo ""
echo "[4/5] Создание коммита..."
read -p "Введите описание изменений (или нажмите Enter для 'Update'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-Update}

git commit -m "$COMMIT_MSG"

echo ""
echo "[5/5] Отправка на GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "========================================"
echo "  Деплой завершен!"
echo "========================================"
echo ""
echo "Mini App будет доступен через 1-2 минуты по адресу:"
echo "https://YOUR_USERNAME.github.io/REPO_NAME/"
echo ""
echo "Не забудьте обновить WEBAPP_URL в keyboards.py!"
echo ""
