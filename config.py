import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database Configuration
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'school_bot.db'

# WebApp Configuration
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://your-webapp-url.com')

# Grading System
MIN_GRADE = 1
MAX_GRADE = 10

# Notification Settings
DEADLINE_REMINDER_DAYS = 1  # Напоминание за 1 день до дедлайна

# Roles
ROLE_TEACHER = 'teacher'
ROLE_PARENT = 'parent'
ROLE_STUDENT = 'student'

# Link Status
LINK_PENDING = 'pending'
LINK_APPROVED = 'approved'
LINK_REJECTED = 'rejected'
