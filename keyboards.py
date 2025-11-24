from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# URL вашего GitHub Pages (обновите после деплоя)
# Формат: https://username.github.io/repository-name/
WEBAPP_URL = "https://YOUR_USERNAME.github.io/school-bot-webapp/"


# ============ MAIN MENUS ============

def get_teacher_menu() -> ReplyKeyboardMarkup:
    """Главное меню учителя"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Ученики"), KeyboardButton(text="📚 Предметы")],
            [KeyboardButton(text="✏️ Выставить оценки"), KeyboardButton(text="📝 Создать ДЗ")],
            [KeyboardButton(text="✅ Одобрить родителей"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(
                text="🌐 Открыть таблицу",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?role=teacher")
            )]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_parent_menu() -> ReplyKeyboardMarkup:
    """Главное меню родителя"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👶 Мои дети")],
            [KeyboardButton(text="📊 Оценки"), KeyboardButton(text="📝 Домашние задания")],
            [KeyboardButton(
                text="🌐 Открыть таблицу",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?role=parent")
            )]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_student_menu() -> ReplyKeyboardMarkup:
    """Главное меню ученика"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Мои оценки"), KeyboardButton(text="📝 Домашние задания")],
            [KeyboardButton(
                text="🌐 Открыть таблицу",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?role=student")
            )]
        ],
        resize_keyboard=True
    )
    return keyboard


# ============ INLINE KEYBOARDS ============

def get_students_keyboard(students: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком учеников"""
    buttons = []
    for student in students:
        buttons.append([InlineKeyboardButton(
            text=f"{student['full_name']} ({student['class_name']})",
            callback_data=f"student_{student['student_id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subjects_keyboard(subjects: list, prefix: str = "subject") -> InlineKeyboardMarkup:
    """Клавиатура со списком предметов"""
    buttons = []
    for subject in subjects:
        buttons.append([InlineKeyboardButton(
            text=subject['name'],
            callback_data=f"{prefix}_{subject['subject_id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_grade_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора оценки (1-10)"""
    buttons = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"grade_{i}"))
        if i % 5 == 0:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_link_approval_keyboard(link_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для одобрения/отклонения связи родитель-ученик"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_link_{link_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_link_{link_id}")
        ]
    ])
    return keyboard


def get_subject_management_keyboard(subject_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для управления предметом"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить предмет", callback_data=f"delete_subject_{subject_id}")]
    ])
    return keyboard


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])
    return keyboard


def get_cancel_button() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    return keyboard


def get_homework_keyboard(homework_id: int, has_file: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для домашнего задания"""
    buttons = []
    if has_file:
        buttons.append([InlineKeyboardButton(text="📎 Скачать файл", callback_data=f"hw_file_{homework_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_hw")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
