from aiogram import Router, F
from aiogram.types import Message

from database import db
from keyboards import get_student_menu
from utils.statistics import get_student_statistics, format_statistics_message

router = Router()


# ============ GRADES ============

@router.message(F.text == "📊 Мои оценки")
async def show_my_grades(message: Message):
    """Показать оценки ученика"""
    # Получение ученика по user_id
    student = db.get_student_by_user_id(message.from_user.id)
    
    if not student:
        await message.answer(
            "❌ Вы не зарегистрированы как ученик в системе.\n\n"
            "Обратитесь к учителю для добавления в систему.",
            reply_markup=get_student_menu()
        )
        return
    
    grades = db.get_student_grades(student['student_id'])
    stats = get_student_statistics(student['student_id'])
    
    if not grades:
        text = "📊 <b>Мои оценки</b>\n\n"
        text += "📝 Оценок пока нет"
    else:
        text = "📊 <b>Мои оценки</b>\n\n"
        text += format_statistics_message(stats)
        text += "\n<b>Последние оценки:</b>\n"
        
        for grade in grades[:15]:  # Показываем последние 15 оценок
            text += f"• {grade['subject_name']}: <b>{grade['grade']}</b> ({grade['date']})\n"
            if grade['comment']:
                text += f"  💬 {grade['comment']}\n"
    
    await message.answer(text, reply_markup=get_student_menu())


# ============ HOMEWORK ============

@router.message(F.text == "📝 Домашние задания")
async def show_homework(message: Message):
    """Показать домашние задания"""
    homework_list = db.get_all_homework()
    
    if not homework_list:
        await message.answer("📝 Домашних заданий пока нет", reply_markup=get_student_menu())
        return
    
    text = "📝 <b>Домашние задания:</b>\n\n"
    
    for hw in homework_list[:15]:  # Показываем последние 15
        text += f"📚 <b>{hw['subject_name']}</b>\n"
        text += f"• {hw['title']}\n"
        text += f"📄 {hw['description']}\n"
        if hw['deadline']:
            text += f"📅 Срок: {hw['deadline']}\n"
        if hw['file_id']:
            text += f"📎 Есть прикрепленный файл\n"
        text += "\n"
    
    await message.answer(text, reply_markup=get_student_menu())
