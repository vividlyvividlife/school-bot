from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from database import db
from keyboards import (
    get_teacher_menu, get_students_keyboard, get_subjects_keyboard,
    get_grade_keyboard, get_link_approval_keyboard, get_cancel_button,
    get_subject_management_keyboard
)
from utils.statistics import get_class_statistics, format_class_statistics_message
from utils.notifications import notify_new_grade, notify_new_homework, notify_link_approved, notify_link_rejected
from config import MIN_GRADE, MAX_GRADE

router = Router()


class TeacherStates(StatesGroup):
    """Состояния для учителя"""
    adding_student_name = State()
    adding_student_class = State()
    adding_subject = State()
    selecting_student_for_grade = State()
    selecting_subject_for_grade = State()
    entering_grade = State()
    entering_grade_comment = State()
    creating_homework_subject = State()
    creating_homework_title = State()
    creating_homework_description = State()
    creating_homework_file = State()
    creating_homework_deadline = State()


# ============ MAIN MENU ============

@router.message(F.text == "👥 Ученики")
async def show_students(message: Message):
    """Показать список учеников"""
    students = db.get_all_students()
    
    if not students:
        await message.answer("📝 Список учеников пуст. Добавьте первого ученика командой /add_student")
        return
    
    text = "👥 <b>Список учеников:</b>\n\n"
    for student in students:
        text += f"• {student['full_name']} ({student['class_name']})\n"
    
    await message.answer(text, reply_markup=get_teacher_menu())


@router.message(Command("add_student"))
async def add_student_start(message: Message, state: FSMContext):
    """Начало добавления ученика"""
    await message.answer("👤 Введите ФИО ученика:", reply_markup=get_cancel_button())
    await state.set_state(TeacherStates.adding_student_name)


@router.message(TeacherStates.adding_student_name)
async def add_student_name(message: Message, state: FSMContext):
    """Получение имени ученика"""
    await state.update_data(student_name=message.text)
    await message.answer("🏫 Введите класс (например, 9А):")
    await state.set_state(TeacherStates.adding_student_class)


@router.message(TeacherStates.adding_student_class)
async def add_student_class(message: Message, state: FSMContext):
    """Получение класса и сохранение ученика"""
    data = await state.get_data()
    student_name = data['student_name']
    class_name = message.text
    
    student_id = db.add_student(student_name, class_name)
    
    if student_id:
        await message.answer(
            f"✅ Ученик <b>{student_name}</b> ({class_name}) успешно добавлен!",
            reply_markup=get_teacher_menu()
        )
    else:
        await message.answer("❌ Ошибка при добавлении ученика", reply_markup=get_teacher_menu())
    
    await state.clear()


# ============ SUBJECTS ============

@router.message(F.text == "📚 Предметы")
async def show_subjects(message: Message):
    """Показать список предметов"""
    subjects = db.get_all_subjects(teacher_id=message.from_user.id)
    
    if not subjects:
        await message.answer(
            "📝 У вас нет предметов. Добавьте первый предмет командой /add_subject",
            reply_markup=get_teacher_menu()
        )
        return
    
    text = "📚 <b>Ваши предметы:</b>\n\n"
    for subject in subjects:
        text += f"• {subject['name']}\n"
    
    await message.answer(text, reply_markup=get_teacher_menu())


@router.message(Command("add_subject"))
async def add_subject_start(message: Message, state: FSMContext):
    """Начало добавления предмета"""
    await message.answer("📚 Введите название предмета:", reply_markup=get_cancel_button())
    await state.set_state(TeacherStates.adding_subject)


@router.message(TeacherStates.adding_subject)
async def add_subject_name(message: Message, state: FSMContext):
    """Получение названия и сохранение предмета"""
    subject_name = message.text
    subject_id = db.add_subject(subject_name, message.from_user.id)
    
    if subject_id:
        await message.answer(
            f"✅ Предмет <b>{subject_name}</b> успешно добавлен!",
            reply_markup=get_teacher_menu()
        )
    else:
        await message.answer("❌ Ошибка при добавлении предмета", reply_markup=get_teacher_menu())
    
    await state.clear()


# ============ GRADES ============

@router.message(F.text == "✏️ Выставить оценки")
async def start_grading(message: Message, state: FSMContext):
    """Начало процесса выставления оценок"""
    students = db.get_all_students()
    
    if not students:
        await message.answer("❌ Нет учеников в системе. Добавьте учеников командой /add_student")
        return
    
    await message.answer("👤 Выберите ученика:", reply_markup=get_students_keyboard(students))
    await state.set_state(TeacherStates.selecting_student_for_grade)


@router.callback_query(TeacherStates.selecting_student_for_grade, F.data.startswith("student_"))
async def select_student_for_grade(callback: CallbackQuery, state: FSMContext):
    """Выбор ученика для оценки"""
    student_id = int(callback.data.split("_")[1])
    await state.update_data(student_id=student_id)
    
    subjects = db.get_all_subjects()
    if not subjects:
        await callback.message.answer("❌ Нет предметов в системе. Добавьте предметы командой /add_subject")
        await state.clear()
        return
    
    student = db.get_student(student_id)
    await callback.message.edit_text(
        f"📚 Выберите предмет для ученика <b>{student['full_name']}</b>:",
        reply_markup=get_subjects_keyboard(subjects, prefix="grade_subject")
    )
    await state.set_state(TeacherStates.selecting_subject_for_grade)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_subject_for_grade, F.data.startswith("grade_subject_"))
async def select_subject_for_grade(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для оценки"""
    subject_id = int(callback.data.split("_")[2])
    await state.update_data(subject_id=subject_id)
    
    await callback.message.edit_text(
        "✏️ Выберите оценку (1-10):",
        reply_markup=get_grade_keyboard()
    )
    await state.set_state(TeacherStates.entering_grade)
    await callback.answer()


@router.callback_query(TeacherStates.entering_grade, F.data.startswith("grade_"))
async def enter_grade(callback: CallbackQuery, state: FSMContext):
    """Получение оценки"""
    grade = int(callback.data.split("_")[1])
    await state.update_data(grade=grade)
    
    await callback.message.edit_text(
        f"Оценка: <b>{grade}</b>\n\n"
        "💬 Введите комментарий к оценке (или отправьте '-' чтобы пропустить):"
    )
    await state.set_state(TeacherStates.entering_grade_comment)
    await callback.answer()


@router.message(TeacherStates.entering_grade_comment)
async def enter_grade_comment(message: Message, state: FSMContext):
    """Получение комментария и сохранение оценки"""
    comment = None if message.text == "-" else message.text
    data = await state.get_data()
    
    student_id = data['student_id']
    subject_id = data['subject_id']
    grade = data['grade']
    
    # Сохранение оценки
    today = datetime.now().strftime('%Y-%m-%d')
    grade_id = db.add_grade(
        student_id=student_id,
        subject_id=subject_id,
        grade=grade,
        teacher_id=message.from_user.id,
        date=today,
        comment=comment
    )
    
    if grade_id:
        student = db.get_student(student_id)
        subjects = db.get_all_subjects()
        subject = next((s for s in subjects if s['subject_id'] == subject_id), None)
        
        # Отправка уведомлений
        parent_links = db.get_parent_students(student_id)
        parent_ids = [link['parent_id'] for link in parent_links]
        
        await notify_new_grade(
            bot=message.bot,
            student_id=student_id,
            parent_ids=parent_ids,
            subject_name=subject['name'],
            grade=grade,
            comment=comment
        )
        
        await message.answer(
            f"✅ Оценка <b>{grade}</b> выставлена ученику <b>{student['full_name']}</b> по предмету <b>{subject['name']}</b>!",
            reply_markup=get_teacher_menu()
        )
    else:
        await message.answer("❌ Ошибка при сохранении оценки", reply_markup=get_teacher_menu())
    
    await state.clear()


# ============ HOMEWORK ============

@router.message(F.text == "📝 Создать ДЗ")
async def create_homework_start(message: Message, state: FSMContext):
    """Начало создания домашнего задания"""
    subjects = db.get_all_subjects(teacher_id=message.from_user.id)
    
    if not subjects:
        await message.answer("❌ Нет предметов. Добавьте предметы командой /add_subject")
        return
    
    await message.answer(
        "📚 Выберите предмет для домашнего задания:",
        reply_markup=get_subjects_keyboard(subjects, prefix="hw_subject")
    )
    await state.set_state(TeacherStates.creating_homework_subject)


@router.callback_query(TeacherStates.creating_homework_subject, F.data.startswith("hw_subject_"))
async def select_homework_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для ДЗ"""
    subject_id = int(callback.data.split("_")[2])
    await state.update_data(subject_id=subject_id)
    
    await callback.message.edit_text("📝 Введите название домашнего задания:")
    await state.set_state(TeacherStates.creating_homework_title)
    await callback.answer()


@router.message(TeacherStates.creating_homework_title)
async def enter_homework_title(message: Message, state: FSMContext):
    """Получение названия ДЗ"""
    await state.update_data(title=message.text)
    await message.answer("📄 Введите описание задания:")
    await state.set_state(TeacherStates.creating_homework_description)


@router.message(TeacherStates.creating_homework_description)
async def enter_homework_description(message: Message, state: FSMContext):
    """Получение описания ДЗ"""
    await state.update_data(description=message.text)
    await message.answer(
        "📎 Прикрепите файл (или отправьте '-' чтобы пропустить):",
        reply_markup=get_cancel_button()
    )
    await state.set_state(TeacherStates.creating_homework_file)


@router.message(TeacherStates.creating_homework_file, F.document)
async def attach_homework_file(message: Message, state: FSMContext):
    """Получение файла для ДЗ"""
    await state.update_data(file_id=message.document.file_id)
    await message.answer("📅 Введите дедлайн (формат: ГГГГ-ММ-ДД ЧЧ:ММ, например: 2025-12-31 23:59):")
    await state.set_state(TeacherStates.creating_homework_deadline)


@router.message(TeacherStates.creating_homework_file, F.text == "-")
async def skip_homework_file(message: Message, state: FSMContext):
    """Пропуск файла"""
    await message.answer("📅 Введите дедлайн (формат: ГГГГ-ММ-ДД ЧЧ:ММ, например: 2025-12-31 23:59):")
    await state.set_state(TeacherStates.creating_homework_deadline)


@router.message(TeacherStates.creating_homework_deadline)
async def enter_homework_deadline(message: Message, state: FSMContext):
    """Получение дедлайна и сохранение ДЗ"""
    data = await state.get_data()
    
    try:
        deadline = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
    except ValueError:
        await message.answer("❌ Неверный формат даты. Попробуйте снова (ГГГГ-ММ-ДД ЧЧ:ММ):")
        return
    
    # Сохранение ДЗ
    homework_id = db.add_homework(
        subject_id=data['subject_id'],
        title=data['title'],
        description=data['description'],
        teacher_id=message.from_user.id,
        deadline=deadline.strftime('%Y-%m-%d %H:%M:%S'),
        file_id=data.get('file_id')
    )
    
    if homework_id:
        subjects = db.get_all_subjects()
        subject = next((s for s in subjects if s['subject_id'] == data['subject_id']), None)
        
        # Отправка уведомлений
        await notify_new_homework(
            bot=message.bot,
            subject_name=subject['name'],
            title=data['title'],
            deadline=message.text
        )
        
        await message.answer(
            f"✅ Домашнее задание <b>{data['title']}</b> создано!",
            reply_markup=get_teacher_menu()
        )
    else:
        await message.answer("❌ Ошибка при создании ДЗ", reply_markup=get_teacher_menu())
    
    await state.clear()


# ============ PARENT-STUDENT LINKS ============

@router.message(F.text == "✅ Одобрить родителей")
async def show_pending_links(message: Message):
    """Показать pending запросы на связь"""
    links = db.get_pending_links()
    
    if not links:
        await message.answer("📝 Нет ожидающих запросов", reply_markup=get_teacher_menu())
        return
    
    for link in links:
        text = f"👨‍👩‍👧 <b>Запрос на связь</b>\n\n"
        text += f"Родитель: <b>{link['parent_name']}</b>\n"
        text += f"Ученик: <b>{link['student_name']}</b>\n"
        text += f"Дата запроса: {link['requested_at']}\n"
        
        await message.answer(text, reply_markup=get_link_approval_keyboard(link['link_id']))


@router.callback_query(F.data.startswith("approve_link_"))
async def approve_link(callback: CallbackQuery):
    """Одобрение связи"""
    link_id = int(callback.data.split("_")[2])
    
    # Получение информации о связи
    links = db.get_pending_links()
    link = next((l for l in links if l['link_id'] == link_id), None)
    
    if not link:
        await callback.answer("❌ Запрос не найден", show_alert=True)
        return
    
    success = db.approve_link(link_id, callback.from_user.id)
    
    if success:
        # Уведомление родителя
        await notify_link_approved(
            bot=callback.bot,
            parent_id=link['parent_id'],
            student_name=link['student_name']
        )
        
        await callback.message.edit_text(
            f"✅ Связь одобрена!\n\n"
            f"Родитель: <b>{link['parent_name']}</b>\n"
            f"Ученик: <b>{link['student_name']}</b>"
        )
    else:
        await callback.answer("❌ Ошибка при одобрении", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("reject_link_"))
async def reject_link(callback: CallbackQuery):
    """Отклонение связи"""
    link_id = int(callback.data.split("_")[2])
    
    # Получение информации о связи
    links = db.get_pending_links()
    link = next((l for l in links if l['link_id'] == link_id), None)
    
    if not link:
        await callback.answer("❌ Запрос не найден", show_alert=True)
        return
    
    success = db.reject_link(link_id, callback.from_user.id)
    
    if success:
        # Уведомление родителя
        await notify_link_rejected(
            bot=callback.bot,
            parent_id=link['parent_id'],
            student_name=link['student_name']
        )
        
        await callback.message.edit_text(
            f"❌ Связь отклонена\n\n"
            f"Родитель: <b>{link['parent_name']}</b>\n"
            f"Ученик: <b>{link['student_name']}</b>"
        )
    else:
        await callback.answer("❌ Ошибка при отклонении", show_alert=True)
    
    await callback.answer()


# ============ STATISTICS ============

@router.message(F.text == "📊 Статистика")
async def show_statistics(message: Message):
    """Показать статистику класса"""
    stats = get_class_statistics()
    text = format_class_statistics_message(stats)
    await message.answer(text, reply_markup=get_teacher_menu())


# ============ CANCEL ============

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена действия"""
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено")
    await callback.answer()
