from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards import get_parent_menu, get_students_keyboard, get_back_button
from utils.statistics import get_student_statistics, format_statistics_message

router = Router()


class ParentStates(StatesGroup):
    """Состояния для родителя"""
    selecting_child = State()
    requesting_link = State()


# ============ MAIN MENU ============

@router.message(F.text == "👶 Мои дети")
async def show_my_children(message: Message):
    """Показать список детей родителя"""
    children = db.get_parent_students(message.from_user.id)
    
    if not children:
        await message.answer(
            "📝 У вас нет привязанных детей.\n\n"
            "Используйте команду /link_child чтобы отправить запрос учителю.",
            reply_markup=get_parent_menu()
        )
        return
    
    text = "👶 <b>Ваши дети:</b>\n\n"
    for child in children:
        text += f"• {child['full_name']} ({child['class_name']})\n"
    
    await message.answer(text, reply_markup=get_parent_menu())


@router.message(F.text.startswith("/link_child"))
async def link_child_start(message: Message, state: FSMContext):
    """Начало процесса связывания с ребенком"""
    students = db.get_all_students()
    
    if not students:
        await message.answer("❌ В системе нет учеников", reply_markup=get_parent_menu())
        return
    
    await message.answer(
        "👤 Выберите вашего ребенка из списка:",
        reply_markup=get_students_keyboard(students)
    )
    await state.set_state(ParentStates.requesting_link)


@router.callback_query(ParentStates.requesting_link, F.data.startswith("student_"))
async def request_link(callback: CallbackQuery, state: FSMContext):
    """Отправка запроса на связь"""
    student_id = int(callback.data.split("_")[1])
    
    # Проверка, не существует ли уже связь
    existing_children = db.get_parent_students(callback.from_user.id)
    if any(child['student_id'] == student_id for child in existing_children):
        await callback.message.edit_text("❌ Вы уже привязаны к этому ученику")
        await state.clear()
        await callback.answer()
        return
    
    # Создание запроса
    link_id = db.create_link_request(callback.from_user.id, student_id)
    
    if link_id:
        student = db.get_student(student_id)
        await callback.message.edit_text(
            f"✅ Запрос отправлен!\n\n"
            f"Ученик: <b>{student['full_name']}</b>\n\n"
            f"Ожидайте одобрения от учителя."
        )
    else:
        await callback.message.edit_text("❌ Ошибка при отправке запроса")
    
    await state.clear()
    await callback.answer()


# ============ GRADES ============

@router.message(F.text == "📊 Оценки")
async def show_grades_menu(message: Message, state: FSMContext):
    """Меню просмотра оценок"""
    children = db.get_parent_students(message.from_user.id)
    
    if not children:
        await message.answer(
            "❌ У вас нет привязанных детей.\n\n"
            "Используйте команду /link_child чтобы отправить запрос учителю.",
            reply_markup=get_parent_menu()
        )
        return
    
    if len(children) == 1:
        # Если один ребенок, сразу показываем оценки
        await show_child_grades(message, children[0]['student_id'])
    else:
        # Если несколько детей, предлагаем выбрать
        await message.answer(
            "👤 Выберите ребенка:",
            reply_markup=get_students_keyboard(children)
        )
        await state.set_state(ParentStates.selecting_child)


@router.callback_query(ParentStates.selecting_child, F.data.startswith("student_"))
async def select_child_for_grades(callback: CallbackQuery, state: FSMContext):
    """Выбор ребенка для просмотра оценок"""
    student_id = int(callback.data.split("_")[1])
    await show_child_grades(callback.message, student_id, edit=True)
    await state.clear()
    await callback.answer()


async def show_child_grades(message: Message, student_id: int, edit: bool = False):
    """Показать оценки ребенка"""
    student = db.get_student(student_id)
    grades = db.get_student_grades(student_id)
    stats = get_student_statistics(student_id)
    
    if not grades:
        text = f"📊 <b>Оценки ученика {student['full_name']}</b>\n\n"
        text += "📝 Оценок пока нет"
    else:
        text = f"📊 <b>Оценки ученика {student['full_name']}</b>\n\n"
        text += format_statistics_message(stats)
        text += "\n<b>Последние оценки:</b>\n"
        
        for grade in grades[:10]:  # Показываем последние 10 оценок
            text += f"• {grade['subject_name']}: <b>{grade['grade']}</b> ({grade['date']})\n"
            if grade['comment']:
                text += f"  💬 {grade['comment']}\n"
    
    if edit:
        await message.edit_text(text, reply_markup=get_back_button())
    else:
        await message.answer(text, reply_markup=get_parent_menu())


# ============ HOMEWORK ============

@router.message(F.text == "📝 Домашние задания")
async def show_homework(message: Message):
    """Показать домашние задания"""
    homework_list = db.get_all_homework()
    
    if not homework_list:
        await message.answer("📝 Домашних заданий пока нет", reply_markup=get_parent_menu())
        return
    
    text = "📝 <b>Домашние задания:</b>\n\n"
    
    for hw in homework_list[:15]:  # Показываем последние 15
        text += f"📚 <b>{hw['subject_name']}</b>\n"
        text += f"• {hw['title']}\n"
        if hw['deadline']:
            text += f"📅 Срок: {hw['deadline']}\n"
        text += "\n"
    
    await message.answer(text, reply_markup=get_parent_menu())


# ============ CALLBACKS ============

@router.callback_query(F.data == "back")
async def back_button(callback: CallbackQuery, state: FSMContext):
    """Кнопка назад"""
    await state.clear()
    await callback.message.delete()
    await callback.answer()
