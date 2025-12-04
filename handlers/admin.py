"""
Обработчики для администратора
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards import get_admin_menu, get_role_selection_keyboard, WEBAPP_URL
from config import ROLE_TEACHER, ROLE_STUDENT, ROLE_PARENT

router = Router()

class AdminStates(StatesGroup):
    creating_invite_name = State()
    creating_class = State()


def get_role_name(role: str) -> str:
    """Получение названия роли на русском"""
    roles = {
        ROLE_TEACHER: 'Учитель',
        ROLE_PARENT: 'Родитель',
        ROLE_STUDENT: 'Ученик'
    }
    return roles.get(role, 'Неизвестно')


# ============ АДМИН ПАНЕЛЬ ============

@router.message(F.text == "⚙️ Админ панель")
async def admin_open_panel(message: Message):
    """Открытие админ панели через inline кнопку (передает initData на всех платформах)"""
    if not db.is_admin(message.from_user.id):
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Открыть Админ панель",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}&role=admin")
        )]
    ])
    
    await message.answer(
        "Нажмите кнопку ниже чтобы открыть админ панель:",
        reply_markup=keyboard
    )


# ============ СОЗДАНИЕ ПРИГЛАШЕНИЙ ============

@router.message(F.text == "🔑 Создать приглашение")
async def admin_create_invite_start(message: Message, state: FSMContext):
    """Начало создания приглашения"""
    if not db.is_admin(message.from_user.id):
        return
    
    await message.answer(
        "Выберите роль для нового пользователя:",
        reply_markup=get_role_selection_keyboard()
    )


@router.callback_query(F.data.startswith("invite_role_"))
async def admin_select_invite_role(callback: CallbackQuery, state: FSMContext):
    """Выбор роли для приглашения"""
    role_map = {
        "invite_role_teacher": ROLE_TEACHER,
        "invite_role_student": ROLE_STUDENT,
        "invite_role_parent": ROLE_PARENT
    }
    
    role = role_map.get(callback.data)
    if not role:
        await callback.answer("Ошибка")
        return
    
    await state.update_data(invite_role=role)
    await callback.message.edit_text(
        f"Введите ФИО для нового пользователя ({get_role_name(role)}):"
    )
    await state.set_state(AdminStates.creating_invite_name)
    await callback.answer()


@router.message(AdminStates.creating_invite_name)
async def admin_create_invite_finish(message: Message, state: FSMContext):
    """Завершение создания приглашения"""
    data = await state.get_data()
    role = data['invite_role']
    full_name = message.text
    
    code = db.create_invite(role, full_name, message.from_user.id)
    
    if code:
        await message.answer(
            f"✅ Приглашение создано!\n\n"
            f"<b>Код:</b> <code>{code}</code>\n"
            f"<b>Роль:</b> {get_role_name(role)}\n"
            f"<b>ФИО:</b> {full_name}\n\n"
            f"Отправьте этот код пользователю.",
            reply_markup=get_admin_menu()
        )
    else:
        await message.answer(
            "❌ Ошибка при создании приглашения",
            reply_markup=get_admin_menu()
        )
    
    await state.clear()


# ============ УПРАВЛЕНИЕ КЛАССАМИ ============

@router.message(F.text == "🏫 Классы")
async def admin_show_classes(message: Message):
    """Показать список классов"""
    if not db.is_admin(message.from_user.id):
        return
    
    classes = db.get_all_classes()
    
    if classes:
        text = "🏫 <b>Классы:</b>\n\n"
        for cls in classes:
            text += f"• {cls['name']}\n"
        text += "\n💡 Для создания нового класса отправьте название (например: 9А)"
    else:
        text = "📝 Классов пока нет.\n\nОтправьте название для создания первого класса (например: 9А)"
    
    await message.answer(text, reply_markup=get_admin_menu())


@router.message(F.text == "📚 Предметы")
async def admin_show_subjects(message: Message):
    """Показать список предметов"""
    if not db.is_admin(message.from_user.id):
        return
    
    subjects = db.get_all_subjects()
    
    if subjects:
        text = "📚 <b>Предметы:</b>\n\n"
        for subj in subjects:
            text += f"• {subj['name']}\n"
    else:
        text = "📝 Предметов пока нет.\n\nИспользуйте команду /add_subject для создания."
    
    await message.answer(text, reply_markup=get_admin_menu())
