// Демо-данные для тестирования Mini App вне Telegram
const DEMO_DATA = {
    students: [
        {
            student_id: 1,
            user_id: 12345,
            full_name: "Иванов Иван",
            parent_id: 54321
        },
        {
            student_id: 2,
            user_id: 12346,
            full_name: "Петрова Мария",
            parent_id: 54322
        },
        {
            student_id: 3,
            user_id: 12347,
            full_name: "Сидоров Петр",
            parent_id: 54321
        }
    ],

    subjects: [
        { subject_id: 1, name: "Математика" },
        { subject_id: 2, name: "Русский язык" },
        { subject_id: 3, name: "Английский язык" },
        { subject_id: 4, name: "Физика" },
        { subject_id: 5, name: "История" }
    ],

    grades: {
        1: [ // Для студента 1
            { grade_id: 1, student_id: 1, subject_id: 1, grade: 5, comment: "Отлично!", date: "2025-11-20" },
            { grade_id: 2, student_id: 1, subject_id: 1, grade: 4, comment: "Хорошо", date: "2025-11-22" },
            { grade_id: 3, student_id: 1, subject_id: 2, grade: 5, comment: "Молодец!", date: "2025-11-21" },
            { grade_id: 4, student_id: 1, subject_id: 3, grade: 4, comment: "", date: "2025-11-23" },
            { grade_id: 5, student_id: 1, subject_id: 4, grade: 3, comment: "Нужно подтянуть", date: "2025-11-24" }
        ],
        2: [ // Для студента 2
            { grade_id: 6, student_id: 2, subject_id: 1, grade: 4, comment: "", date: "2025-11-20" },
            { grade_id: 7, student_id: 2, subject_id: 2, grade: 5, comment: "Отлично!", date: "2025-11-21" },
            { grade_id: 8, student_id: 2, subject_id: 3, grade: 5, comment: "Превосходно!", date: "2025-11-22" }
        ],
        3: [ // Для студента 3
            { grade_id: 9, student_id: 3, subject_id: 1, grade: 3, comment: "", date: "2025-11-20" },
            { grade_id: 10, student_id: 3, subject_id: 2, grade: 4, comment: "", date: "2025-11-21" },
            { grade_id: 11, student_id: 3, subject_id: 5, grade: 5, comment: "Отличная работа!", date: "2025-11-23" }
        ]
    },

    homework: [
        {
            homework_id: 1,
            subject_id: 1,
            subject_name: "Математика",
            title: "Решить задачи",
            description: "Учебник стр. 45, номера 1-10",
            deadline: "2025-11-26T23:59:00",
            file_id: null
        },
        {
            homework_id: 2,
            subject_id: 2,
            subject_name: "Русский язык",
            title: "Сочинение",
            description: "Написать сочинение на тему 'Моя семья' (200 слов)",
            deadline: "2025-11-28T23:59:00",
            file_id: null
        },
        {
            homework_id: 3,
            subject_id: 3,
            subject_name: "Английский язык",
            title: "Выучить слова",
            description: "Unit 5, новые слова (20 штук)",
            deadline: "2025-11-25T20:00:00",
            file_id: null
        }
    ],

    statistics: {
        1: {
            overall_average: 4.2,
            total_grades: 5,
            subject_averages: {
                "Математика": { average: 4.5, count: 2, last_grade: 4 },
                "Русский язык": { average: 5.0, count: 1, last_grade: 5 },
                "Английский язык": { average: 4.0, count: 1, last_grade: 4 },
                "Физика": { average: 3.0, count: 1, last_grade: 3 }
            }
        },
        2: {
            overall_average: 4.67,
            total_grades: 3,
            subject_averages: {
                "Математика": { average: 4.0, count: 1, last_grade: 4 },
                "Русский язык": { average: 5.0, count: 1, last_grade: 5 },
                "Английский язык": { average: 5.0, count: 1, last_grade: 5 }
            }
        },
        3: {
            overall_average: 4.0,
            total_grades: 3,
            subject_averages: {
                "Математика": { average: 3.0, count: 1, last_grade: 3 },
                "Русский язык": { average: 4.0, count: 1, last_grade: 4 },
                "История": { average: 5.0, count: 1, last_grade: 5 }
            }
        }
    },

    parent_students: {
        54321: [1, 3], // Родитель 54321 имеет детей со student_id 1 и 3
        54322: [2]     // Родитель 54322 имеет ребенка со student_id 2
    }
};
