@echo off
REM Скрипт для деплоя Mini App на GitHub Pages

echo ========================================
echo   School Bot - GitHub Pages Deploy
echo ========================================
echo.

REM Проверка наличия Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git не установлен!
    echo Скачайте Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] Переход в директорию webapp...
cd webapp

REM Проверка наличия .git
if not exist ".git" (
    echo.
    echo [2/5] Инициализация Git репозитория...
    git init
    
    echo.
    echo [!] Введите URL вашего GitHub репозитория:
    echo Формат: https://github.com/USERNAME/REPO_NAME.git
    set /p REPO_URL="URL: "
    
    git remote add origin %REPO_URL%
) else (
    echo [2/5] Git репозиторий уже инициализирован
)

echo.
echo [3/5] Добавление файлов...
git add .

echo.
echo [4/5] Создание коммита...
set /p COMMIT_MSG="Введите описание изменений (или нажмите Enter для 'Update'): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update

git commit -m "%COMMIT_MSG%"

echo.
echo [5/5] Отправка на GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo   Деплой завершен!
echo ========================================
echo.
echo Mini App будет доступен через 1-2 минуты по адресу:
echo https://YOUR_USERNAME.github.io/REPO_NAME/
echo.
echo Не забудьте обновить WEBAPP_URL в keyboards.py!
echo.
pause
