"""
Простой веб-сервер для Mini App
Запускается вместе с ботом и отдает статические файлы
"""

from aiohttp import web
import os
from pathlib import Path

# Путь к webapp
WEBAPP_DIR = Path(__file__).parent / 'webapp'


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


def create_webapp_server(host='0.0.0.0', port=8080):
    """Создание веб-сервера для Mini App"""
    app = web.Application()
    
    # Маршруты
    app.router.add_get('/', serve_index)
    app.router.add_get('/index.html', serve_index)
    app.router.add_get('/css/{filename}', serve_static)
    app.router.add_get('/js/{filename}', serve_static)
    
    # Статические файлы
    app.router.add_static('/css/', WEBAPP_DIR / 'css', name='css')
    app.router.add_static('/js/', WEBAPP_DIR / 'js', name='js')
    
    return app, host, port


async def start_webapp_server(app, host, port):
    """Запуск веб-сервера"""
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"📱 Mini App server started at http://{host}:{port}")
    return runner


if __name__ == '__main__':
    # Тестовый запуск
    app, host, port = create_webapp_server()
    web.run_app(app, host=host, port=port)
