import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT, LINK_PENDING

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Создает подключение к базе данных"""
        # check_same_thread=False нужен, так как мы используем asyncio.to_thread
        # timeout=10 увеличивает время ожидания разблокировки базы
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица учеников
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT NOT NULL,
                class_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица связей родитель-ученик
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parent_student_links (
                link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                approved_by INTEGER,
                FOREIGN KEY (parent_id) REFERENCES users(user_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (approved_by) REFERENCES users(user_id)
            )
        ''')

        # Таблица предметов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                max_grade INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица оценок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                grade INTEGER NOT NULL,
                date DATE NOT NULL,
                comment TEXT,
                teacher_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
                FOREIGN KEY (teacher_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица домашних заданий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS homework (
                homework_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                file_id TEXT,
                deadline TIMESTAMP,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')

        # === НОВЫЕ ТАБЛИЦЫ ДЛЯ ПОЛНОЦЕННОЙ ШКОЛЫ ===
        
        # Таблица классов (9А, 10Б и т.д.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица назначений учителей (кто какой предмет в каком классе ведет)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teaching_assignments (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(teacher_id, class_id, subject_id),
                FOREIGN KEY (teacher_id) REFERENCES users(user_id),
                FOREIGN KEY (class_id) REFERENCES classes(class_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
            )
        ''')
        
        # Таблица пригласительных кодов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invite_codes (
                code_id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                used_by INTEGER,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                FOREIGN KEY (used_by) REFERENCES users(user_id),
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')
        
        # Добавляем колонку is_admin в таблицу users (если еще нет)
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0')
        except:
            pass  # Колонка уже существует

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    # ============ USER METHODS ============
    
    def add_user(self, user_id: int, username: Optional[str], full_name: str, role: str) -> bool:
        """Добавление нового пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (user_id, username, full_name, role) VALUES (?, ?, ?, ?)',
                (user_id, username, full_name, role)
            )
            conn.commit()
            conn.close()
            logger.info(f"User {user_id} added with role {role}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {user_id} already exists")
            return False

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def is_first_user(self) -> bool:
        """Проверка, является ли это первым пользователем"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        count = cursor.fetchone()['count']
        conn.close()
        return count == 0

    def update_user_role(self, user_id: int, role: str) -> bool:
        """Обновление роли пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', (role, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False

    # ============ STUDENT METHODS ============
    
    def add_student(self, full_name: str, class_name: str, user_id: Optional[int] = None) -> Optional[int]:
        """Добавление ученика"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO students (user_id, full_name, class_name) VALUES (?, ?, ?)',
                (user_id, full_name, class_name)
            )
            student_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Student {full_name} added with ID {student_id}")
            return student_id
        except Exception as e:
            logger.error(f"Error adding student: {e}")
            return None

    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации об ученике"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_students(self) -> List[Dict[str, Any]]:
        """Получение списка всех учеников"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students ORDER BY class_name, full_name')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_student_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение ученика по user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # ============ PARENT-STUDENT LINK METHODS ============
    
    def create_link_request(self, parent_id: int, student_id: int) -> Optional[int]:
        """Создание запроса на связь родитель-ученик"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO parent_student_links (parent_id, student_id, status) VALUES (?, ?, ?)',
                (parent_id, student_id, LINK_PENDING)
            )
            link_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Link request created: parent {parent_id} -> student {student_id}")
            return link_id
        except Exception as e:
            logger.error(f"Error creating link request: {e}")
            return None

    def get_pending_links(self) -> List[Dict[str, Any]]:
        """Получение всех pending запросов на связь"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, u.full_name as parent_name, s.full_name as student_name
            FROM parent_student_links l
            JOIN users u ON l.parent_id = u.user_id
            JOIN students s ON l.student_id = s.student_id
            WHERE l.status = 'pending'
            ORDER BY l.requested_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def approve_link(self, link_id: int, teacher_id: int) -> bool:
        """Одобрение связи родитель-ученик"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE parent_student_links SET status = ?, approved_at = ?, approved_by = ? WHERE link_id = ?',
                ('approved', datetime.now(), teacher_id, link_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"Link {link_id} approved by teacher {teacher_id}")
            return True
        except Exception as e:
            logger.error(f"Error approving link: {e}")
            return False

    def reject_link(self, link_id: int, teacher_id: int) -> bool:
        """Отклонение связи родитель-ученик"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE parent_student_links SET status = ?, approved_by = ? WHERE link_id = ?',
                ('rejected', teacher_id, link_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"Link {link_id} rejected by teacher {teacher_id}")
            return True
        except Exception as e:
            logger.error(f"Error rejecting link: {e}")
            return False

    def get_parent_students(self, parent_id: int) -> List[Dict[str, Any]]:
        """Получение учеников родителя (только approved)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*
            FROM students s
            JOIN parent_student_links l ON s.student_id = l.student_id
            WHERE l.parent_id = ? AND l.status = 'approved'
        ''', (parent_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ============ SUBJECT METHODS ============
    
    def add_subject(self, name: str, teacher_id: int, max_grade: int = 10) -> Optional[int]:
        """Добавление предмета"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO subjects (name, teacher_id, max_grade) VALUES (?, ?, ?)',
                (name, teacher_id, max_grade)
            )
            subject_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Subject {name} added with ID {subject_id}, max_grade={max_grade}")
            return subject_id
        except Exception as e:
            logger.error(f"Error adding subject: {e}")
            return None

    def get_all_subjects(self, teacher_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получение всех предметов (опционально фильтр по учителю)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if teacher_id:
            cursor.execute('SELECT * FROM subjects WHERE teacher_id = ? ORDER BY name', (teacher_id,))
        else:
            cursor.execute('SELECT * FROM subjects ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_subject(self, subject_id: int) -> bool:
        """Удаление предмета"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM subjects WHERE subject_id = ?', (subject_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting subject: {e}")
            return False

    # ============ GRADE METHODS ============
    
    def add_grade(self, student_id: int, subject_id: int, grade: int, 
                  teacher_id: int, date: str, comment: Optional[str] = None) -> Optional[int]:
        """Добавление оценки"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO grades (student_id, subject_id, grade, date, comment, teacher_id) VALUES (?, ?, ?, ?, ?, ?)',
                (student_id, subject_id, grade, date, comment, teacher_id)
            )
            grade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Grade {grade} added for student {student_id}")
            return grade_id
        except Exception as e:
            logger.error(f"Error adding grade: {e}")
            return None

    def get_student_grades(self, student_id: int) -> List[Dict[str, Any]]:
        """Получение всех оценок ученика"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.*, s.name as subject_name
            FROM grades g
            JOIN subjects s ON g.subject_id = s.subject_id
            WHERE g.student_id = ?
            ORDER BY g.date DESC
        ''', (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_grades_by_subject(self, student_id: int, subject_id: int) -> List[Dict[str, Any]]:
        """Получение оценок ученика по предмету"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM grades
            WHERE student_id = ? AND subject_id = ?
            ORDER BY date DESC
        ''', (student_id, subject_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_grade(self, grade_id: int, grade: int, comment: Optional[str] = None) -> bool:
        """Обновление оценки"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE grades SET grade = ?, comment = ? WHERE grade_id = ?',
                (grade, comment, grade_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"Grade {grade_id} updated to {grade}")
            return True
        except Exception as e:
            logger.error(f"Error updating grade: {e}")
            return False

    # ============ HOMEWORK METHODS ============
    
    def add_homework(self, subject_id: int, title: str, description: str,
                     teacher_id: int, deadline: Optional[str] = None, 
                     file_id: Optional[str] = None) -> Optional[int]:
        """Добавление домашнего задания"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO homework (subject_id, title, description, file_id, deadline, created_by) VALUES (?, ?, ?, ?, ?, ?)',
                (subject_id, title, description, file_id, deadline, teacher_id)
            )
            homework_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Homework {title} added with ID {homework_id}")
            return homework_id
        except Exception as e:
            logger.error(f"Error adding homework: {e}")
            return None

    def get_all_homework(self, subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получение всех домашних заданий (опционально фильтр по предмету)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if subject_id:
            cursor.execute('''
                SELECT h.*, s.name as subject_name
                FROM homework h
                JOIN subjects s ON h.subject_id = s.subject_id
                WHERE h.subject_id = ?
                ORDER BY h.deadline ASC
            ''', (subject_id,))
        else:
            cursor.execute('''
                SELECT h.*, s.name as subject_name
                FROM homework h
                JOIN subjects s ON h.subject_id = s.subject_id
                ORDER BY h.deadline ASC
            ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_homework(self, homework_id: int) -> Optional[Dict[str, Any]]:
        """Получение конкретного домашнего задания"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.*, s.name as subject_name
            FROM homework h
            JOIN subjects s ON h.subject_id = s.subject_id
            WHERE h.homework_id = ?
        ''', (homework_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # ============ ADMIN METHODS ============
    
    def is_first_user(self) -> bool:
        """Проверка, является ли БД пустой (для создания первого админа)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        count = cursor.fetchone()['count']
        conn.close()
        return count == 0
    
    def make_admin(self, user_id: int) -> bool:
        """Назначить пользователя админом"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error making user admin: {e}")
            return False
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь админом"""
        user = self.get_user(user_id)
        return user and user.get('is_admin', 0) == 1
    
    # --- Управление классами ---
    
    def create_class(self, name: str) -> Optional[int]:
        """Создать класс"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO classes (name) VALUES (?)', (name,))
            class_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return class_id
        except sqlite3.IntegrityError:
            logger.warning(f"Class {name} already exists")
            return None
    
    def get_all_classes(self) -> List[Dict[str, Any]]:
        """Получить все классы"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM classes ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # --- Управление назначениями ---
    
    def assign_teacher(self, teacher_id: int, class_id: int, subject_id: int) -> Optional[int]:
        """Назначить учителя на предмет в классе"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO teaching_assignments (teacher_id, class_id, subject_id)
                VALUES (?, ?, ?)
            ''', (teacher_id, class_id, subject_id))
            assignment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return assignment_id
        except sqlite3.IntegrityError:
            logger.warning(f"Assignment already exists")
            return None
    
    def get_teacher_assignments(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Получить все назначения учителя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ta.*, c.name as class_name, s.name as subject_name
            FROM teaching_assignments ta
            JOIN classes c ON ta.class_id = c.class_id
            JOIN subjects s ON ta.subject_id = s.subject_id
            WHERE ta.teacher_id = ?
            ORDER BY c.name, s.name
        ''', (teacher_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # --- Управление приглашениями ---
    
    def generate_invite_code(self) -> str:
        """Генерация уникального кода приглашения"""
        import secrets
        import string
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(8))
    
    def create_invite(self, role: str, full_name: str, created_by: int) -> str:
        """Создать пригласительный код"""
        code = self.generate_invite_code()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO invite_codes (code, role, full_name, created_by)
                VALUES (?, ?, ?, ?)
            ''', (code, role, full_name, created_by))
            conn.commit()
            conn.close()
            return code
        except Exception as e:
            logger.error(f"Error creating invite: {e}")
            return None
    
    def use_invite_code(self, code: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Использовать пригласительный код"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем код
        cursor.execute('''
            SELECT * FROM invite_codes 
            WHERE code = ? AND is_used = 0
        ''', (code,))
        invite = cursor.fetchone()
        
        if not invite:
            conn.close()
            return None
        
        # Помечаем код как использованный
        cursor.execute('''
            UPDATE invite_codes 
            SET is_used = 1, used_by = ?, used_at = CURRENT_TIMESTAMP
            WHERE code = ?
        ''', (user_id, code))
        
        conn.commit()
        conn.close()
        
        return {
            'role': invite['role'],
            'full_name': invite['full_name']
        }


# Singleton instance
db = Database()
