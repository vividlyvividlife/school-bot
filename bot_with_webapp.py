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
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT
from database import db
from keyboards import get_admin_menu, get_teacher_menu, get_parent_menu, get_student_menu

# Import handlers
from handlers import teacher, parent, student, admin

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

# FSM States
class RegistrationStates(StatesGroup):
    waiting_for_code = State()

# Middleware для логирования
@dp.update.outer_middleware
async def logging_middleware(handler, event, data):
    if event.message and event.message.text:
        logger.info(f"📩 Message: '{event.message.text}' from {event.message.from_user.id}")
    elif event.callback_query:
        logger.info(f"📩 Callback: '{event.callback_query.data}' from {event.callback_query.from_user.id}")
    return await handler(event, data)


@main_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    user = db.get_user(message.from_user.id)
    
    if user:
        # Пользователь уже зарегистрирован
        role = user['role']
        is_admin = db.is_admin(message.from_user.id)
        
        if is_admin:
            await message.answer(
                f"👋 С возвращением, <b>{user['full_name']}</b>!\n\n"
                f"Вы - <b>Администратор</b> школы.",
                reply_markup=get_admin_menu()
            )
        else:
            await message.answer(
                f"👋 С возвращением, <b>{user['full_name']}</b>!\n\n"
                f"Ваша роль: <b>{get_role_name(role)}</b>",
                reply_markup=get_menu_by_role(role)
            )
    else:
        # Проверяем, первый ли это пользователь
        if db.is_first_user():
            # Первый пользователь становится админом
            db.add_user(
                message.from_user.id,
                message.from_user.username,
                message.from_user.full_name or "Администратор",
                ROLE_ADMIN
            )
            db.make_admin(message.from_user.id)
            
            await message.answer(
                "👑 <b>Система инициализирована!</b>\n\n"
                "Вы назначены <b>Администратором</b> школы.\n"
                "Используйте меню для управления классами и пользователями.",
                reply_markup=get_admin_menu()
            )
        else:
            # Обычный пользователь - просим код приглашения
            await message.answer(
                "👋 Добро пожаловать в School Bot!\n\n"
                "Для доступа к системе введите <b>Код Приглашения</b>, полученный от администратора:"
            )
            await state.set_state(RegistrationStates.waiting_for_code)


# Обработка кода приглашения
@main_router.message(RegistrationStates.waiting_for_code)
async def process_invite_code(message: Message, state: FSMContext):
    """Обработка кода приглашения"""
    code = message.text.strip().upper()
    
    invite_data = db.use_invite_code(code, message.from_user.id)
    
    if invite_data:
        # Регистрируем пользователя
        db.add_user(
            message.from_user.id,
            message.from_user.username,
            invite_data['full_name'],
            invite_data['role']
        )
        
        await state.clear()
        await message.answer(
            f"✅ Код принят!\n\n"
            f"Добро пожаловать, <b>{invite_data['full_name']}</b>.\n"
            f"Ваша роль: <b>{get_role_name(invite_data['role'])}</b>",
            reply_markup=get_menu_by_role(invite_data['role'])
        )
    else:
        await message.answer(
            "❌ Неверный код или он уже использован.\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )



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
        ROLE_STUDENT: 'Ученик',
        ROLE_ADMIN: 'Администратор'
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
    dp.include_router(admin.router)
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
