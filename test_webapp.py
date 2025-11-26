"""
Запуск веб-сервера отдельно для тестирования Mini App
"""

import logging
from aiohttp import web
from webapp_server import create_webapp_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Запуск только веб-сервера"""
    app, host, port = create_webapp_server(host='0.0.0.0', port=8080)
    
    logger.info(f"🚀 Starting Mini App server...")
    logger.info(f"📱 Open http://localhost:{port}?role=teacher in your browser")
    logger.info(f"📱 Or http://localhost:{port}?role=parent for parent view")
    logger.info(f"📱 Or http://localhost:{port}?role=student for student view")
    logger.info(f"Press Ctrl+C to stop")
    
    web.run_app(app, host=host, port=port)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
