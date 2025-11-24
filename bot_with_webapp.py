"""
Бот с интегрированным веб-сервером для Mini App
Запускает и бота, и веб-сервер одновременно
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT
from database import db
from keyboards import get_teacher_menu, get_parent_menu, get_student_menu

# Import handlers
from handlers import teacher, parent, student

# Import webapp server
from webapp_server import create_webapp_server, start_webapp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Main router
main_router = Router()


@main_router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user = db.get_user(message.from_user.id)
    
    if user:
        # Пользователь уже зарегистрирован
        role = user['role']
        await message.answer(
            f"👋 С возвращением, <b>{user['full_name']}</b>!\n\n"
            f"Ваша роль: <b>{get_role_name(role)}</b>",
            reply_markup=get_menu_by_role(role)
        )
    else:
        # Новый пользователь
        await message.answer(
            "👋 Добро пожаловать в School Bot!\n\n"
            "Пожалуйста, введите ваше ФИО:"
        )


@main_router.message(F.text, ~F.text.startswith('/'))
async def handle_registration(message: Message):
    """Обработка регистрации нового пользователя"""
    user = db.get_user(message.from_user.id)
    
    if user:
        # Пользователь уже зарегистрирован, игнорируем
        return
    
    # Проверка, первый ли это пользователь
    is_first = db.is_first_user()
    role = ROLE_TEACHER if is_first else ROLE_PARENT
    
    # Регистрация пользователя
    success = db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.text,
        role=role
    )
    
    if success:
        if is_first:
            await message.answer(
                f"✅ Вы зарегистрированы как <b>Учитель</b>!\n\n"
                f"Вы первый пользователь системы и получили роль учителя.\n\n"
                f"Используйте меню ниже для управления:",
                reply_markup=get_teacher_menu()
            )
        else:
            await message.answer(
                f"✅ Вы зарегистрированы как <b>Родитель</b>!\n\n"
                f"Используйте команду /link_child чтобы привязать ребенка.\n\n"
                f"Если вы ученик, обратитесь к учителю для изменения роли.",
                reply_markup=get_parent_menu()
            )
    else:
        await message.answer("❌ Ошибка при регистрации. Попробуйте позже.")


@main_router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка по командам"""
    user = db.get_user(message.from_user.id)
    
    if not user:
        await message.answer("Пожалуйста, сначала зарегистрируйтесь с помощью /start")
        return
    
    role = user['role']
    
    if role == ROLE_TEACHER:
        help_text = """
📚 <b>Команды учителя:</b>

/add_student - Добавить ученика
/add_subject - Добавить предмет

<b>Меню:</b>
👥 Ученики - Список учеников
📚 Предметы - Список предметов
✏️ Выставить оценки - Выставление оценок
📝 Создать ДЗ - Создание домашнего задания
✅ Одобрить родителей - Одобрение запросов
📊 Статистика - Статистика класса
🌐 Открыть таблицу - Mini App интерфейс
        """
    elif role == ROLE_PARENT:
        help_text = """
👨‍👩‍👧 <b>Команды родителя:</b>

/link_child - Привязать ребенка

<b>Меню:</b>
👶 Мои дети - Список детей
📊 Оценки - Просмотр оценок
📝 Домашние задания - Список ДЗ
🌐 Открыть таблицу - Mini App интерфейс
        """
    else:  # STUDENT
        help_text = """
🎓 <b>Команды ученика:</b>

<b>Меню:</b>
📊 Мои оценки - Просмотр оценок
📝 Домашние задания - Список ДЗ
🌐 Открыть таблицу - Mini App интерфейс
        """
    
    await message.answer(help_text)


def get_role_name(role: str) -> str:
    """Получение названия роли на русском"""
    roles = {
        ROLE_TEACHER: 'Учитель',
        ROLE_PARENT: 'Родитель',
        ROLE_STUDENT: 'Ученик'
    }
    return roles.get(role, 'Неизвестно')


def get_menu_by_role(role: str):
    """Получение меню по роли"""
    if role == ROLE_TEACHER:
        return get_teacher_menu()
    elif role == ROLE_PARENT:
        return get_parent_menu()
    else:
        return get_student_menu()


async def main():
    """Запуск бота и веб-сервера"""
    # Register routers
    dp.include_router(main_router)
    dp.include_router(teacher.router)
    dp.include_router(parent.router)
    dp.include_router(student.router)
    
    # Create webapp server
    webapp_app, host, port = create_webapp_server(host='0.0.0.0', port=8080)
    
    # Start webapp server
    webapp_runner = await start_webapp_server(webapp_app, host, port)
    
    logger.info("🤖 Bot started")
    logger.info(f"📱 Mini App available at http://localhost:{port}")
    logger.info("💡 Use ngrok to make it public: ngrok http 8080")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await webapp_runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
