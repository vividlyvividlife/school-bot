"""
Test script to verify database functionality
"""

from database import db
from config import ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT
from datetime import datetime, timedelta

def test_database():
    print("🧪 Testing School Bot Database\n")
    
    # Test 1: Add users
    print("1️⃣ Testing user registration...")
    teacher_id = 111111111
    parent_id = 222222222
    student_user_id = 333333333
    
    db.add_user(teacher_id, "teacher_user", "Иванова Мария Петровна", ROLE_TEACHER)
    db.add_user(parent_id, "parent_user", "Петров Иван Сергеевич", ROLE_PARENT)
    db.add_user(student_user_id, "student_user", "Петрова Анна Ивановна", ROLE_STUDENT)
    
    teacher = db.get_user(teacher_id)
    print(f"✅ Teacher created: {teacher['full_name']} (role: {teacher['role']})")
    
    # Test 2: Add students
    print("\n2️⃣ Testing student management...")
    student1_id = db.add_student("Петрова Анна Ивановна", "9А", student_user_id)
    student2_id = db.add_student("Сидоров Петр Алексеевич", "9А")
    student3_id = db.add_student("Козлова Елена Дмитриевна", "9Б")
    
    students = db.get_all_students()
    print(f"✅ Added {len(students)} students")
    for s in students:
        print(f"   - {s['full_name']} ({s['class_name']})")
    
    # Test 3: Add subjects
    print("\n3️⃣ Testing subject management...")
    math_id = db.add_subject("Математика", teacher_id)
    russian_id = db.add_subject("Русский язык", teacher_id)
    physics_id = db.add_subject("Физика", teacher_id)
    
    subjects = db.get_all_subjects()
    print(f"✅ Added {len(subjects)} subjects")
    for s in subjects:
        print(f"   - {s['name']}")
    
    # Test 4: Add grades
    print("\n4️⃣ Testing grade management...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Grades for student 1
    db.add_grade(student1_id, math_id, 9, teacher_id, today, "Отличная работа!")
    db.add_grade(student1_id, math_id, 8, teacher_id, today)
    db.add_grade(student1_id, russian_id, 10, teacher_id, today, "Превосходно!")
    db.add_grade(student1_id, physics_id, 7, teacher_id, today)
    
    # Grades for student 2
    db.add_grade(student2_id, math_id, 6, teacher_id, today)
    db.add_grade(student2_id, russian_id, 8, teacher_id, today)
    
    grades = db.get_student_grades(student1_id)
    print(f"✅ Added grades for students")
    print(f"   Student 1 has {len(grades)} grades")
    
    # Test 5: Parent-student link
    print("\n5️⃣ Testing parent-student linking...")
    link_id = db.create_link_request(parent_id, student1_id)
    print(f"✅ Link request created (ID: {link_id})")
    
    pending = db.get_pending_links()
    print(f"   Pending requests: {len(pending)}")
    
    db.approve_link(link_id, teacher_id)
    print(f"✅ Link approved")
    
    parent_children = db.get_parent_students(parent_id)
    print(f"   Parent has {len(parent_children)} linked children")
    
    # Test 6: Add homework
    print("\n6️⃣ Testing homework management...")
    deadline = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    
    hw1_id = db.add_homework(
        math_id,
        "Решить задачи 1-10",
        "Учебник стр. 45, задачи 1-10. Показать решение.",
        teacher_id,
        deadline
    )
    
    hw2_id = db.add_homework(
        russian_id,
        "Сочинение",
        "Написать сочинение на тему 'Моя семья' (200-300 слов)",
        teacher_id,
        deadline
    )
    
    homework = db.get_all_homework()
    print(f"✅ Added {len(homework)} homework assignments")
    for hw in homework:
        print(f"   - {hw['subject_name']}: {hw['title']}")
    
    # Test 7: Statistics
    print("\n7️⃣ Testing statistics...")
    from utils.statistics import get_student_statistics, get_class_statistics
    
    stats = get_student_statistics(student1_id)
    print(f"✅ Student 1 statistics:")
    print(f"   Overall average: {stats['overall_average']}")
    print(f"   Total grades: {stats['total_grades']}")
    print(f"   Subject averages:")
    for subject, data in stats['subject_averages'].items():
        print(f"      - {subject}: {data['average']} ({data['count']} grades)")
    
    class_stats = get_class_statistics("9А")
    print(f"\n✅ Class 9А statistics:")
    print(f"   Total students: {class_stats['total_students']}")
    print(f"   Top 3 students:")
    for i, student in enumerate(class_stats['student_rankings'][:3], 1):
        print(f"      {i}. {student['full_name']}: {student['average']}")
    
    print("\n" + "="*50)
    print("✅ All tests passed successfully!")
    print("="*50)

if __name__ == "__main__":
    test_database()
