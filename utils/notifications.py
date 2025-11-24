from aiogram import Bot
from typing import List
import logging

logger = logging.getLogger(__name__)


async def notify_new_grade(bot: Bot, student_id: int, parent_ids: List[int], 
                          subject_name: str, grade: int, comment: str = None):
    """Уведомление о новой оценке"""
    message = f"📊 <b>Новая оценка!</b>\n\n"
    message += f"Предмет: <b>{subject_name}</b>\n"
    message += f"Оценка: <b>{grade}</b>\n"
    if comment:
        message += f"Комментарий: {comment}\n"
    
    # Уведомление ученика
    from database import db
    student = db.get_student(student_id)
    if student and student['user_id']:
        try:
            await bot.send_message(student['user_id'], message)
        except Exception as e:
            logger.error(f"Failed to notify student {student_id}: {e}")
    
    # Уведомление родителей
    for parent_id in parent_ids:
        try:
            await bot.send_message(parent_id, message)
        except Exception as e:
            logger.error(f"Failed to notify parent {parent_id}: {e}")


async def notify_new_homework(bot: Bot, subject_name: str, title: str, 
                             deadline: str = None):
    """Уведомление о новом домашнем задании"""
    from database import db
    
    message = f"📝 <b>Новое домашнее задание!</b>\n\n"
    message += f"Предмет: <b>{subject_name}</b>\n"
    message += f"Задание: {title}\n"
    if deadline:
        message += f"📅 Срок сдачи: <b>{deadline}</b>\n"
    
    # Получение всех учеников и родителей
    students = db.get_all_students()
    notified = set()
    
    for student in students:
        # Уведомление ученика
        if student['user_id'] and student['user_id'] not in notified:
            try:
                await bot.send_message(student['user_id'], message)
                notified.add(student['user_id'])
            except Exception as e:
                logger.error(f"Failed to notify student {student['student_id']}: {e}")
        
        # Уведомление родителей ученика
        parent_links = db.get_parent_students(student['student_id'])
        for link in parent_links:
            parent_id = link.get('parent_id')
            if parent_id and parent_id not in notified:
                try:
                    await bot.send_message(parent_id, message)
                    notified.add(parent_id)
                except Exception as e:
                    logger.error(f"Failed to notify parent {parent_id}: {e}")


async def notify_link_approved(bot: Bot, parent_id: int, student_name: str):
    """Уведомление об одобрении связи"""
    message = f"✅ <b>Запрос одобрен!</b>\n\n"
    message += f"Вы теперь можете просматривать оценки и домашние задания ученика <b>{student_name}</b>."
    
    try:
        await bot.send_message(parent_id, message)
    except Exception as e:
        logger.error(f"Failed to notify parent {parent_id}: {e}")


async def notify_link_rejected(bot: Bot, parent_id: int, student_name: str):
    """Уведомление об отклонении связи"""
    message = f"❌ <b>Запрос отклонен</b>\n\n"
    message += f"Ваш запрос на просмотр данных ученика <b>{student_name}</b> был отклонен учителем."
    
    try:
        await bot.send_message(parent_id, message)
    except Exception as e:
        logger.error(f"Failed to notify parent {parent_id}: {e}")


async def notify_deadline_reminder(bot: Bot, homework_id: int):
    """Напоминание о дедлайне (за 1 день)"""
    from database import db
    
    homework = db.get_homework(homework_id)
    if not homework:
        return
    
    message = f"⏰ <b>Напоминание о дедлайне!</b>\n\n"
    message += f"Предмет: <b>{homework['subject_name']}</b>\n"
    message += f"Задание: {homework['title']}\n"
    message += f"📅 Срок сдачи: <b>{homework['deadline']}</b>\n"
    
    # Уведомление всех учеников
    students = db.get_all_students()
    for student in students:
        if student['user_id']:
            try:
                await bot.send_message(student['user_id'], message)
            except Exception as e:
                logger.error(f"Failed to send deadline reminder to student {student['student_id']}: {e}")
