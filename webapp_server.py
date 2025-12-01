"""
Простой веб-сервер для Mini App с REST API
Запускается вместе с ботом и отдает статические файлы + API endpoints
Updated: 2025-11-28 - Added user role API endpoint
"""

from aiohttp import web
import aiohttp_cors
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from database import db
from utils.statistics import get_student_statistics

logger = logging.getLogger(__name__)

# Путь к webapp
WEBAPP_DIR = Path(__file__).parent / 'webapp'


# ============ STATIC FILES ============

async def serve_index(request):
    """Отдача index.html"""
    index_path = WEBAPP_DIR / 'index.html'
    return web.FileResponse(index_path)


async def serve_static(request):
    """Отдача статических файлов (CSS, JS)"""
    filename = request.match_info['filename']
    filepath = request.match_info.get('filepath', '')
    
    # Безопасность: проверка на выход за пределы директории
    full_path = WEBAPP_DIR / filepath / filename
    if not full_path.is_file():
        return web.Response(status=404, text='File not found')
    
    return web.FileResponse(full_path)


# ============ API HANDLERS ============

async def api_get_user(request):
    """Получение информации о пользователе по telegram_id"""
    user_id = int(request.match_info['user_id'])
    logger.info(f"API: GET /api/user/{user_id}")
    try:
        # user_id здесь это telegram_id из фронтенда
        user = await asyncio.to_thread(db.get_user, user_id)
        if not user:
            return web.json_response({'success': False, 'error': 'User not found'}, status=404)
        
        # Проверяем является ли админом
        is_admin = await asyncio.to_thread(db.is_admin, user_id)
        user['is_admin'] = is_admin
        
        return web.json_response({'success': True, 'data': user})
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_students(request):
    """Получение списка учеников"""
    logger.info(f"API: GET /api/students")
    try:
        # Запускаем синхронную работу с БД в отдельном потоке
        students = await asyncio.to_thread(db.get_all_students)
        return web.json_response({'success': True, 'data': students})
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_student(request):
    """Получение данных ученика"""
    student_id = int(request.match_info['student_id'])
    logger.info(f"API: GET /api/students/{student_id}")
    try:
        student = await asyncio.to_thread(db.get_student, student_id)
        if not student:
            return web.json_response({'success': False, 'error': 'Student not found'}, status=404)
        return web.json_response({'success': True, 'data': student})
    except Exception as e:
        logger.error(f"Error getting student: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_subjects(request):
    """Получение списка предметов"""
    logger.info(f"API: GET /api/subjects")
    try:
        subjects = await asyncio.to_thread(db.get_all_subjects)
        return web.json_response({'success': True, 'data': subjects})
    except Exception as e:
        logger.error(f"Error getting subjects: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_grades(request):
    """Получение оценок ученика"""
    student_id = request.query.get('student_id')
    logger.info(f"API: GET /api/grades student_id={student_id}")
    
    if not student_id:
        return web.json_response({'success': False, 'error': 'student_id is required'}, status=400)
    
    try:
        grades = await asyncio.to_thread(db.get_student_grades, int(student_id))
        return web.json_response({'success': True, 'data': grades})
    except Exception as e:
        logger.error(f"Error getting grades: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_add_grade(request):
    """Добавление оценки"""
    logger.info(f"API: POST /api/grades")
    try:
        data = await request.json()
        logger.info(f"API: Adding grade data: {data}")
        
        student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        grade = data.get('grade')
        comment = data.get('comment')
        teacher_id = data.get('teacher_id')
        
        if not all([student_id, subject_id, grade, teacher_id]):
            return web.json_response({'success': False, 'error': 'Missing required fields'}, status=400)
            
        success = await asyncio.to_thread(
            db.add_grade,
            student_id=int(student_id),
            subject_id=int(subject_id),
            grade=int(grade),
            comment=comment,
            teacher_id=int(teacher_id)
        )
        
        if success:
            logger.info("API: Grade added successfully")
            return web.json_response({'success': True})
        else:
            logger.error("API: Failed to add grade (db error)")
            return web.json_response({'success': False, 'error': 'Failed to add grade'}, status=500)
    except Exception as e:
        logger.error(f"Error adding grade: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_update_grade(request):
    """Обновление оценки"""
    grade_id = int(request.match_info['grade_id'])
    logger.info(f"API: PUT /api/grades/{grade_id}")
    try:
        data = await request.json()
        grade = data.get('grade')
        comment = data.get('comment')
        
        if grade is None:
            return web.json_response({'success': False, 'error': 'Grade is required'}, status=400)
            
        success = await asyncio.to_thread(db.update_grade, grade_id, int(grade), comment)
        
        if success:
            return web.json_response({'success': True})
        else:
            return web.json_response({'success': False, 'error': 'Failed to update grade'}, status=500)
    except Exception as e:
        logger.error(f"Error updating grade: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_homework(request):
    """Получение домашнего задания"""
    subject_id = request.query.get('subject_id')
    logger.info(f"API: GET /api/homework subject_id={subject_id}")
    try:
        if subject_id:
            homework = await asyncio.to_thread(db.get_homework, int(subject_id))
        else:
            homework = [] 
            
        return web.json_response({'success': True, 'data': homework})
    except Exception as e:
        logger.error(f"Error getting homework: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_statistics(request):
    """Получение статистики"""
    student_id = request.query.get('student_id')
    logger.info(f"API: GET /api/statistics student_id={student_id}")
    
    if not student_id:
        return web.json_response({'success': False, 'error': 'student_id is required'}, status=400)
        
    try:
        stats = await asyncio.to_thread(get_student_statistics, int(student_id))
        return web.json_response({'success': True, 'data': stats})
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def api_get_parent_students(request):
    """Получение детей родителя"""
    parent_id = int(request.match_info['parent_id'])
    logger.info(f"API: GET /api/parent/{parent_id}/students")
    try:
        students = await asyncio.to_thread(db.get_parent_students, parent_id)
        return web.json_response({'success': True, 'data': students})
    except Exception as e:
        logger.error(f"Error getting parent students: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_user(request):
    """Получение информации о пользователе"""
    user_id = int(request.match_info['user_id'])
    logger.info(f"API: GET /api/user/{user_id}")
    try:
        user = await asyncio.to_thread(db.get_user, user_id)
        if not user:
            return web.json_response({'success': False, 'error': 'User not found'}, status=404)
        return web.json_response({'success': True, 'data': user})
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_add_subject(request):
    """Создание предмета"""
    logger.info(f"API: POST /api/subjects")
    try:
        data = await request.json()
        name = data.get('name')
        teacher_id = data.get('teacher_id')
        max_grade = data.get('max_grade', 10)
        
        if not name or not teacher_id:
            return web.json_response({'success': False, 'error': 'Name and teacher_id are required'}, status=400)
        
        subject_id = await asyncio.to_thread(db.add_subject, name, int(teacher_id), int(max_grade))
        if subject_id:
            return web.json_response({'success': True, 'data': {'subject_id': subject_id}})
        else:
            return web.json_response({'success': False, 'error': 'Failed to add subject'}, status=500)
    except Exception as e:
        logger.error(f"Error adding subject: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_add_student(request):
    """Создание ученика"""
    logger.info(f"API: POST /api/students")
    try:
        data = await request.json()
        full_name = data.get('full_name')
        class_name = data.get('class_name')
        user_id = data.get('user_id')  # Optional
        
        if not full_name or not class_name:
            return web.json_response({'success': False, 'error': 'full_name and class_name are required'}, status=400)
        
        student_id = await asyncio.to_thread(db.add_student, full_name, class_name, user_id)
        if student_id:
            return web.json_response({'success': True, 'data': {'student_id': student_id}})
        else:
            return web.json_response({'success': False, 'error': 'Failed to add student'}, status=500)
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_add_homework(request):
    """Создание домашнего задания"""
    logger.info(f"API: POST /api/homework")
    try:
        data = await request.json()
        subject_id = data.get('subject_id')
        title = data.get('title')
        description = data.get('description', '')
        deadline = data.get('deadline')
        teacher_id = data.get('teacher_id')
        
        if not subject_id or not title or not teacher_id:
            return web.json_response({'success': False, 'error': 'subject_id, title, and teacher_id are required'}, status=400)
        
        homework_id = await asyncio.to_thread(
            db.add_homework,
            int(subject_id),
            title,
            description,
            int(teacher_id),
            deadline
        )
        if homework_id:
            return web.json_response({'success': True, 'data': {'homework_id': homework_id}})
        else:
            return web.json_response({'success': False, 'error': 'Failed to add homework'}, status=500)
    except Exception as e:
        logger.error(f"Error adding homework: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


# ============ SERVER SETUP ============

def create_webapp_server(host='0.0.0.0', port=8080):
    """Создание веб-сервера для Mini App"""
    app = web.Application()
    
    # Настройка CORS для доступа с GitHub Pages и других доменов
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
    })
    
    # Static routes
    static_routes = [
        app.router.add_get('/', serve_index),
        app.router.add_get('/index.html', serve_index),
    ]
    
    # Static files (не добавляем CORS к статическим файлам)
    app.router.add_static('/css/', WEBAPP_DIR / 'css', name='css')
    app.router.add_static('/js/', WEBAPP_DIR / 'js', name='js')
    
    # API routes (с CORS)
    api_routes = [
        app.router.add_get('/api/students', api_get_students),
        app.router.add_get('/api/students/{student_id}', api_get_student),
        app.router.add_get('/api/subjects', api_get_subjects),
        app.router.add_get('/api/grades', api_get_grades),
        app.router.add_post('/api/grades', api_add_grade),
        app.router.add_put('/api/grades/{grade_id}', api_update_grade),
        app.router.add_get('/api/homework', api_get_homework),
        app.router.add_get('/api/statistics', api_get_statistics),
        app.router.add_get('/api/parent/{parent_id}/students', api_get_parent_students),
        app.router.add_get('/api/user/{user_id}', api_get_user),
        app.router.add_post('/api/subjects', api_add_subject),
        app.router.add_post('/api/students', api_add_student),
        app.router.add_post('/api/homework', api_add_homework),
    ]
    
    # Применяем CORS к API роутам
    for route in api_routes:
        cors.add(route)
    
    logger.info("✅ CORS configured for API routes")
    
    return app, host, port


async def start_webapp_server(app, host, port):
    """Запуск веб-сервера"""
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"📱 Mini App server started at http://{host}:{port}")
    logger.info(f"📡 API available at http://{host}:{port}/api")
    return runner


if __name__ == '__main__':
    # Тестовый запуск
    logging.basicConfig(level=logging.INFO)
    app, host, port = create_webapp_server()
    web.run_app(app, host=host, port=port)
