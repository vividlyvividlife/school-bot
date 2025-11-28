"""
Скрипт для добавления тестовых данных в базу данных
Запустите этот файл чтобы добавить демо-данные для тестирования
"""

from database import db
from config import ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT
from datetime import datetime, timedelta
import random

def add_demo_data(teacher_id=None):
    print("🚀 Добавление тестовых данных...")
    
    # 1. Определяем ID учителя
    if teacher_id is None:
        # Если не передан, используем первого пользователя или создаем дефолтного
        if db.is_first_user():
            teacher_id = 111111
            db.add_user(
                user_id=teacher_id,
                username="teacher_demo",
                full_name="Иван Иванович Учителев",
                role=ROLE_TEACHER
            )
            print(f"✅ Добавлен учитель ID: {teacher_id}")
        else:
            # Попробуем найти существующего учителя
            teacher_id = 111111
            print(f"ℹ️ Используем учителя ID: {teacher_id}")
    else:
        print(f"ℹ️ Используем учителя ID: {teacher_id} (из параметра)")
    
    # 2. Добавляем родителей
    parent_ids = [222222, 333333]
    for i, parent_id in enumerate(parent_ids, 1):
        try:
            db.add_user(
                user_id=parent_id,
                username=f"parent_{i}",
                full_name=f"Родитель {i}",
                role=ROLE_PARENT
            )
            print(f"✅ Добавлен родитель ID: {parent_id}")
        except Exception as e:
            print(f"⚠️ Родитель {parent_id} уже существует")
    
    # 3. Добавляем учеников
    students_data = [
        {"full_name": "Петров Петр Петрович", "class_name": "9А"},
        {"full_name": "Сидорова Мария Ивановна", "class_name": "9А"},
        {"full_name": "Иванов Иван Сергеевич", "class_name": "9Б"},
        {"full_name": "Козлова Анна Дмитриевна", "class_name": "9Б"},
        {"full_name": "Смирнов Алексей Владимирович", "class_name": "10А"},
    ]
    
    student_ids = []
    for student_data in students_data:
        student_id = db.add_student(
            full_name=student_data["full_name"],
            class_name=student_data["class_name"]
        )
        if student_id:
            student_ids.append(student_id)
            print(f"✅ Добавлен ученик: {student_data['full_name']} (ID: {student_id})")
    
    # 4. Связываем родителей с учениками
    if len(student_ids) >= 2:
        # Родитель 1 -> Ученик 1
        link_id = db.create_link_request(parent_ids[0], student_ids[0])
        if link_id:
            db.approve_link(link_id, teacher_id)
            print(f"✅ Родитель {parent_ids[0]} связан с учеником {student_ids[0]}")
        
        # Родитель 2 -> Ученик 2
        link_id = db.create_link_request(parent_ids[1], student_ids[1])
        if link_id:
            db.approve_link(link_id, teacher_id)
            print(f"✅ Родитель {parent_ids[1]} связан с учеником {student_ids[1]}")
    
    # 5. Добавляем предметы
    subjects_data = ["Математика", "Русский язык", "Физика", "Химия", "История"]
    subject_ids = []
    
    for subject_name in subjects_data:
        subject_id = db.add_subject(name=subject_name, teacher_id=teacher_id)
        if subject_id:
            subject_ids.append(subject_id)
            print(f"✅ Добавлен предмет: {subject_name} (ID: {subject_id})")
    
    # 6. Добавляем оценки
    print("\n📝 Добавление оценок...")
    today = datetime.now()
    
    for student_id in student_ids:
        for subject_id in subject_ids:
            # Добавляем 5-10 оценок для каждого предмета
            num_grades = random.randint(5, 10)
            for i in range(num_grades):
                grade = random.randint(3, 10)  # Оценки от 3 до 10
                days_ago = random.randint(1, 60)
                date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                comments = [
                    "Хорошая работа",
                    "Нужно подтянуть",
                    "Отлично!",
                    "Молодец",
                    "Контрольная работа",
                    "Самостоятельная работа",
                    ""
                ]
                comment = random.choice(comments)
                
                grade_id = db.add_grade(
                    student_id=student_id,
                    subject_id=subject_id,
                    grade=grade,
                    teacher_id=teacher_id,
                    date=date,
                    comment=comment
                )
    
    print("✅ Оценки добавлены")
    
    # 7. Добавляем домашние задания
    print("\n📚 Добавление домашних заданий...")
    homework_data = [
        {
            "subject_id": subject_ids[0] if subject_ids else 1,
            "title": "Решить задачи 1-10",
            "description": "Решить задачи из учебника стр. 45-50",
            "deadline": (today + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            "subject_id": subject_ids[1] if len(subject_ids) > 1 else 1,
            "title": "Написать сочинение",
            "description": "Тема: 'Мое любимое время года'",
            "deadline": (today + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            "subject_id": subject_ids[2] if len(subject_ids) > 2 else 1,
            "title": "Лабораторная работа",
            "description": "Провести эксперимент и оформить отчет",
            "deadline": (today + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for hw in homework_data:
        hw_id = db.add_homework(
            subject_id=hw["subject_id"],
            title=hw["title"],
            description=hw["description"],
            teacher_id=teacher_id,
            deadline=hw["deadline"]
        )
        if hw_id:
            print(f"✅ Добавлено ДЗ: {hw['title']}")
    
    print("\n✨ Тестовые данные успешно добавлены!")
    print("\n📊 Статистика:")
    print(f"👥 Учеников: {len(student_ids)}")
    print(f"📚 Предметов: {len(subject_ids)}")
    print(f"📝 Домашних заданий: {len(homework_data)}")
    print(f"\n🔑 Используйте для входа:")
    print(f"   Учитель ID: {teacher_id}")
    print(f"   Родитель 1 ID: {parent_ids[0]}")
    print(f"   Родитель 2 ID: {parent_ids[1]}")


if __name__ == "__main__":
    import sys
    # Можно передать teacher_id как аргумент: python add_demo_data.py 479339411
    teacher_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    add_demo_data(teacher_id)
