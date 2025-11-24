from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import db


def calculate_average_grade(grades: List[Dict[str, Any]]) -> float:
    """Вычисление среднего балла"""
    if not grades:
        return 0.0
    total = sum(g['grade'] for g in grades)
    return round(total / len(grades), 2)


def get_student_statistics(student_id: int) -> Dict[str, Any]:
    """Получение статистики ученика"""
    grades = db.get_student_grades(student_id)
    subjects = db.get_all_subjects()
    
    stats = {
        'overall_average': calculate_average_grade(grades),
        'total_grades': len(grades),
        'subject_averages': {}
    }
    
    # Средний балл по каждому предмету
    for subject in subjects:
        subject_grades = [g for g in grades if g['subject_id'] == subject['subject_id']]
        if subject_grades:
            stats['subject_averages'][subject['name']] = {
                'average': calculate_average_grade(subject_grades),
                'count': len(subject_grades),
                'last_grade': subject_grades[0]['grade'] if subject_grades else None
            }
    
    return stats


def get_grade_dynamics(student_id: int, subject_id: int, days: int = 30) -> List[Dict[str, Any]]:
    """Получение динамики оценок за период"""
    grades = db.get_grades_by_subject(student_id, subject_id)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_grades = [
        g for g in grades 
        if datetime.strptime(g['date'], '%Y-%m-%d') >= cutoff_date
    ]
    
    # Группировка по неделям
    weekly_data = {}
    for grade in recent_grades:
        date = datetime.strptime(grade['date'], '%Y-%m-%d')
        week = date.strftime('%Y-W%W')
        
        if week not in weekly_data:
            weekly_data[week] = []
        weekly_data[week].append(grade['grade'])
    
    # Вычисление средних по неделям
    dynamics = []
    for week, grades_list in sorted(weekly_data.items()):
        dynamics.append({
            'week': week,
            'average': round(sum(grades_list) / len(grades_list), 2),
            'count': len(grades_list)
        })
    
    return dynamics


def get_class_statistics(class_name: str = None) -> Dict[str, Any]:
    """Получение статистики по классу"""
    students = db.get_all_students()
    if class_name:
        students = [s for s in students if s['class_name'] == class_name]
    
    stats = {
        'total_students': len(students),
        'student_rankings': []
    }
    
    # Рейтинг учеников
    for student in students:
        student_stats = get_student_statistics(student['student_id'])
        stats['student_rankings'].append({
            'student_id': student['student_id'],
            'full_name': student['full_name'],
            'average': student_stats['overall_average'],
            'total_grades': student_stats['total_grades']
        })
    
    # Сортировка по среднему баллу
    stats['student_rankings'].sort(key=lambda x: x['average'], reverse=True)
    
    return stats


def format_statistics_message(stats: Dict[str, Any]) -> str:
    """Форматирование статистики для отправки пользователю"""
    message = f"📊 <b>Статистика</b>\n\n"
    message += f"📈 Общий средний балл: <b>{stats['overall_average']}</b>\n"
    message += f"📝 Всего оценок: <b>{stats['total_grades']}</b>\n\n"
    
    if stats['subject_averages']:
        message += "<b>По предметам:</b>\n"
        for subject_name, subject_stats in stats['subject_averages'].items():
            message += f"• {subject_name}: <b>{subject_stats['average']}</b> "
            message += f"({subject_stats['count']} оценок)\n"
    
    return message


def format_class_statistics_message(stats: Dict[str, Any]) -> str:
    """Форматирование статистики класса"""
    message = f"📊 <b>Статистика класса</b>\n\n"
    message += f"👥 Всего учеников: <b>{stats['total_students']}</b>\n\n"
    
    if stats['student_rankings']:
        message += "<b>Рейтинг учеников:</b>\n"
        for i, student in enumerate(stats['student_rankings'][:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {student['full_name']}: <b>{student['average']}</b>\n"
    
    return message
