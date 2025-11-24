@echo off
chcp 65001 >nul
echo ==========================================
echo   Заливка проекта на GitHub
echo ==========================================
echo.

REM Проверка Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Git не установлен!
    pause
    exit /b
)

echo 1. Инициализация репозитория...
if not exist ".git" (
    git init
) else (
    echo Репозиторий уже инициализирован.
)

echo.
echo 2. Добавление файлов...
git add .

echo.
echo 3. Создание коммита...
git commit -m "Initial commit: School Bot setup"

echo.
echo 4. Настройка ветки main...
git branch -M main

echo.
echo ==========================================
echo ВАЖНО: Создайте пустой репозиторий на https://github.com/new
echo и скопируйте ссылку (https://github.com/user/repo.git)
echo ==========================================
echo.

set /p REPO_URL="Вставьте ссылку на репозиторий: "

echo.
echo 5. Привязка удаленного репозитория...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo.
echo 6. Отправка кода на GitHub...
git push -u origin main

echo.
if errorlevel 0 (
    echo [УСПЕХ] Код успешно отправлен!
    echo Теперь настройте Secrets в GitHub Actions для деплоя на VDS.
) else (
    echo [ОШИБКА] Не удалось отправить код. Проверьте ссылку и доступ.
)

pause
