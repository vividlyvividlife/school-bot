"""
Простой веб-сервер для Mini App с REST API
Запускается вместе с ботом и отдает статические файлы + API endpoints
"""

from aiohttp import web
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


# ============ API ENDPOINTS ============

async def api_get_students(request):
    """GET /api/students - Получение списка учеников"""
    try:
        students = db.get_all_students()
        return web.json_response({'success': True, 'data': students})
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_student(request):
    """GET /api/students/{student_id} - Получение конкретного ученика"""
    try:
        student_id = int(request.match_info['student_id'])
        student = db.get_student(student_id)
        
        if not student:
            return web.json_response({'success': False, 'error': 'Student not found'}, status=404)
        
        return web.json_response({'success': True, 'data': student})
    except Exception as e:
        logger.error(f"Error getting student: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_subjects(request):
    """GET /api/subjects - Получение списка предметов"""
    try:
        teacher_id = request.query.get('teacher_id')
        subjects = db.get_all_subjects(teacher_id=int(teacher_id) if teacher_id else None)
        return web.json_response({'success': True, 'data': subjects})
    except Exception as e:
        logger.error(f"Error getting subjects: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_grades(request):
    """GET /api/grades?student_id={id} - Получение оценок ученика"""
    try:
        student_id = int(request.query.get('student_id'))
        grades = db.get_student_grades(student_id)
        return web.json_response({'success': True, 'data': grades})
    except Exception as e:
        logger.error(f"Error getting grades: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_add_grade(request):
    """POST /api/grades - Добавление оценки"""
    try:
        data = await request.json()
        
        student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        grade = data.get('grade')
        teacher_id = data.get('teacher_id')
        comment = data.get('comment', '')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not all([student_id, subject_id, grade, teacher_id]):
            return web.json_response({'success': False, 'error': 'Missing required fields'}, status=400)
        
        grade_id = db.add_grade(
            student_id=student_id,
            subject_id=subject_id,
            grade=grade,
            teacher_id=teacher_id,
            date=date,
            comment=comment
        )
        
        if grade_id:
            return web.json_response({'success': True, 'grade_id': grade_id})
        else:
            return web.json_response({'success': False, 'error': 'Failed to add grade'}, status=500)
    except Exception as e:
        logger.error(f"Error adding grade: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_update_grade(request):
    """PUT /api/grades/{grade_id} - Обновление оценки"""
    try:
        grade_id = int(request.match_info['grade_id'])
        data = await request.json()
        
        grade = data.get('grade')
        comment = data.get('comment', '')
        
        if not grade:
            return web.json_response({'success': False, 'error': 'Grade is required'}, status=400)
        
        success = db.update_grade(grade_id, grade, comment)
        
        if success:
            return web.json_response({'success': True, 'message': 'Grade updated successfully'})
        else:
            return web.json_response({'success': False, 'error': 'Failed to update grade'}, status=500)
    except Exception as e:
        logger.error(f"Error updating grade: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_homework(request):
    """GET /api/homework - Получение домашних заданий"""
    try:
        subject_id = request.query.get('subject_id')
        homework = db.get_all_homework(subject_id=int(subject_id) if subject_id else None)
        return web.json_response({'success': True, 'data': homework})
    except Exception as e:
        logger.error(f"Error getting homework: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_statistics(request):
    """GET /api/statistics?student_id={id} - Получение статистики ученика"""
    try:
        student_id = int(request.query.get('student_id'))
        stats = get_student_statistics(student_id)
        return web.json_response({'success': True, 'data': stats})
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_get_parent_students(request):
    """GET /api/parent/{parent_id}/students - Получение детей родителя"""
    try:
        parent_id = int(request.match_info['parent_id'])
        students = db.get_parent_students(parent_id)
        return web.json_response({'success': True, 'data': students})
    except Exception as e:
        logger.error(f"Error getting parent students: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


# ============ SERVER SETUP ============

def create_webapp_server(host='0.0.0.0', port=8080):
    """Создание веб-сервера для Mini App"""
    app = web.Application()
    
    # Static routes
    app.router.add_get('/', serve_index)
    app.router.add_get('/index.html', serve_index)
    app.router.add_get('/css/{filename}', serve_static)
    app.router.add_get('/js/{filename}', serve_static)
    
    # Static files
    app.router.add_static('/css/', WEBAPP_DIR / 'css', name='css')
    app.router.add_static('/js/', WEBAPP_DIR / 'js', name='js')
    
    # API routes
    app.router.add_get('/api/students', api_get_students)
    app.router.add_get('/api/students/{student_id}', api_get_student)
    app.router.add_get('/api/subjects', api_get_subjects)
    app.router.add_get('/api/grades', api_get_grades)
    app.router.add_post('/api/grades', api_add_grade)
    app.router.add_put('/api/grades/{grade_id}', api_update_grade)
    app.router.add_get('/api/homework', api_get_homework)
    app.router.add_get('/api/statistics', api_get_statistics)
    app.router.add_get('/api/parent/{parent_id}/students', api_get_parent_students)
    
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
