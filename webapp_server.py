"""
Простой веб-сервер для Mini App с REST API
Запускается вместе с ботом и отдает статические файлы + API endpoints
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
        app.router.add_get('/css/{filename}', serve_static),
        app.router.add_get('/js/{filename}', serve_static),
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
