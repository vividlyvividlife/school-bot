# 🚀 Шпаргалка по деплою School Bot

## 📦 Первоначальная настройка

### 1. Настройка VDS сервера

```bash
# Подключитесь к VDS
ssh user@your-vds-ip

# Создайте директорию
sudo mkdir -p /botSchool
sudo chown $USER:$USER /botSchool

# Клонируйте репозиторий
cd /botSchool
git clone https://github.com/YOUR_USERNAME/school-bot.git .

# Создайте .env
nano .env
```

Содержимое `.env`:
```
BOT_TOKEN=your_bot_token_from_botfather
WEBAPP_URL=https://YOUR_USERNAME.github.io/school-bot/
```

### 2. Первый запуск на VDS

```bash
cd /botSchool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
screen -dmS school_bot bash -c "source venv/bin/activate && python bot.py"
```

### 3. Настройка GitHub Secrets

В репозитории: **Settings** → **Secrets and variables** → **Actions**

Добавьте:
- `VDS_HOST` = IP вашего VDS
- `VDS_USERNAME` = имя пользователя
- `VDS_SSH_KEY` = приватный SSH ключ
- `VDS_PORT` = 22 (или другой SSH порт)

### 4. Включите GitHub Pages

**Settings** → **Pages** → Source: **GitHub Actions**

---

## 🔄 Ежедневное использование

### Обновление кода

```bash
# Внесите изменения
git add .
git commit -m "Update: описание"
git push origin main

# GitHub Actions автоматически задеплоит на VDS и GitHub Pages
```

### Просмотр логов на VDS

```bash
ssh user@your-vds-ip

# Логи деплоя
tail -f /botSchool/deploy.log

# Логи бота
tail -f /botSchool/bot.log

# Подключиться к screen сессии
screen -r school_bot
# Отключиться: Ctrl+A, затем D
```

### Перезапуск бота вручную

```bash
ssh user@your-vds-ip
screen -X -S school_bot quit
cd /botSchool
screen -dmS school_bot bash -c "source venv/bin/activate && python bot.py"
```

---

## 🛠️ Полезные команды

### Git

```bash
# Статус
git status

# Посмотреть изменения
git diff

# Отменить изменения
git checkout -- filename

# Создать ветку
git checkout -b feature/new-feature

# Переключиться на main
git checkout main

# Обновить локальную копию
git pull origin main
```

### Screen (на VDS)

```bash
# Список сессий
screen -ls

# Создать новую сессию
screen -S session_name

# Подключиться к сессии
screen -r session_name

# Отключиться (не закрывая)
Ctrl+A, затем D

# Убить сессию
screen -X -S session_name quit
```

### Python/Pip

```bash
# Активировать venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Обновить pip
pip install --upgrade pip

# Посмотреть установленные пакеты
pip list
```

---

## 🔍 Проверка статуса

### Проверка бота на VDS

```bash
ssh user@your-vds-ip

# Запущен ли screen?
screen -ls | grep school_bot

# Последние 50 строк лога
tail -n 50 /botSchool/bot.log

# Следить за логом в реальном времени
tail -f /botSchool/bot.log
```

### Проверка GitHub Actions

1. Откройте репозиторий на GitHub
2. Вкладка **Actions**
3. Посмотрите статус последних runs

### Проверка GitHub Pages

Откройте: `https://YOUR_USERNAME.github.io/school-bot/`

---

## ❗ Troubleshooting

### Бот не запускается

```bash
# Проверьте логи
tail -f /botSchool/bot.log

# Проверьте .env
cat /botSchool/.env

# Проверьте зависимости
cd /botSchool
source venv/bin/activate
pip list | grep aiogram
```

### GitHub Actions падает

1. Проверьте логи в Actions
2. Проверьте GitHub Secrets
3. Проверьте SSH подключение:
   ```bash
   ssh -i ~/.ssh/your_key user@vds-ip
   ```

### Mini App не обновляется

1. Проверьте, что изменились файлы в `webapp/`
2. Посмотрите логи в GitHub Actions
3. Очистите кеш браузера

---

## 📝 Чеклист перед деплоем

- [ ] Тесты проходят локально (`python test_db.py`)
- [ ] `.env` файл не коммитится
- [ ] `WEBAPP_URL` обновлен в `keyboards.py`
- [ ] GitHub Secrets настроены
- [ ] VDS сервер доступен по SSH
- [ ] GitHub Pages включен

---

## 🎯 Быстрые ссылки

- **Репозиторий**: https://github.com/YOUR_USERNAME/school-bot
- **GitHub Actions**: https://github.com/YOUR_USERNAME/school-bot/actions
- **Mini App**: https://YOUR_USERNAME.github.io/school-bot/
- **BotFather**: https://t.me/BotFather

---

**Сохраните эту шпаргалку!** 📌
