# 🚀 Быстрый старт - GitHub Pages

## Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. Название: `school-bot-webapp`
3. Тип: **Public**
4. Нажмите **Create repository**

## Шаг 2: Запустите скрипт деплоя

### Windows:
```bash
deploy_github.bat
```

### Linux/Mac:
```bash
chmod +x deploy_github.sh
./deploy_github.sh
```

Скрипт спросит URL репозитория. Введите:
```
https://github.com/YOUR_USERNAME/school-bot-webapp.git
```

## Шаг 3: Включите GitHub Pages

1. Откройте репозиторий на GitHub
2. **Settings** → **Pages**
3. Source: `main` branch, `/ (root)` folder
4. Нажмите **Save**

## Шаг 4: Обновите URL в боте

Откройте `keyboards.py` и замените:

```python
WEBAPP_URL = "https://YOUR_USERNAME.github.io/school-bot-webapp/"
```

Замените `YOUR_USERNAME` на ваш GitHub username.

## Шаг 5: Запустите бота

```bash
python bot.py
```

## ✅ Готово!

Откройте бота в Telegram и нажмите **🌐 Открыть таблицу**

---

## 🔄 Обновление Mini App

После изменений в `webapp/`:

```bash
cd webapp
git add .
git commit -m "Update"
git push
```

Изменения появятся через 1-2 минуты.

---

**Подробная инструкция:** [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md)
