// API helper для связи с Telegram Bot
// Работает через Telegram WebApp API

const API = {
    // Проверка, запущено ли приложение в Telegram
    isTelegramWebApp() {
        return window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData;
    },

    // Проверка демо-режима
    isDemoMode() {
        return !this.isTelegramWebApp() && typeof DEMO_DATA !== 'undefined';
    },

    // Получение данных пользователя из Telegram
    getUserData(userId) {
        // Если демо-режим, возвращаем тестовые данные
        if (this.isDemoMode()) {
            return {
                user_id: userId || 12345,
                username: 'demo_user',
                full_name: 'Демо Пользователь',
                role: this.getRoleFromParam(null)
            };
        }

        // Данные передаются через initData от Telegram
        const tg = window.Telegram.WebApp;
        const user = tg.initDataUnsafe.user;

        // В реальном приложении роль будет получена от бота
        // Для демо используем start_param из deep link
        const startParam = tg.initDataUnsafe.start_param;

        return {
            user_id: user.id,
            username: user.username,
            full_name: `${user.first_name} ${user.last_name || ''}`.trim(),
            role: this.getRoleFromParam(startParam)
        };
    },

    getRoleFromParam(param) {
        // Роль передается через start_param при открытии Mini App
        // Формат: role_teacher, role_parent, role_student
        if (!param) return 'parent';

        if (param.includes('teacher')) return 'teacher';
        if (param.includes('student')) return 'student';
        return 'parent';
    },

    // Отправка данных обратно в бот
    sendDataToBot(action, data) {
        const tg = window.Telegram.WebApp;
        const payload = {
            action: action,
            data: data,
            timestamp: Date.now()
        };

        // Отправка данных боту
        tg.sendData(JSON.stringify(payload));
    },

    // Получение данных через CloudStorage (Telegram)
    async getFromStorage(key) {
        return new Promise((resolve) => {
            window.Telegram.WebApp.CloudStorage.getItem(key, (error, value) => {
                if (error) {
                    console.error('Storage error:', error);
                    resolve(null);
                } else {
                    resolve(value ? JSON.parse(value) : null);
                }
            });
        });
    },

    // Сохранение данных в CloudStorage
    async saveToStorage(key, value) {
        return new Promise((resolve) => {
            window.Telegram.WebApp.CloudStorage.setItem(
                key,
                JSON.stringify(value),
                (error, success) => {
                    if (error) {
                        console.error('Storage error:', error);
                        resolve(false);
                    } else {
                        resolve(true);
                    }
                }
            );
        });
    },

    // Получение списка учеников
    async getStudents() {
        if (this.isDemoMode()) {
            return DEMO_DATA.students;
        }

        const cached = await this.getFromStorage('students');
        if (cached) return cached;

        // Если нет в кеше, запрашиваем у бота
        this.requestDataFromBot('get_students');
        return [];
    },

    async getStudent(studentId) {
        const students = await this.getStudents();
        return students.find(s => s.student_id === studentId);
    },

    async getSubjects() {
        if (this.isDemoMode()) {
            return DEMO_DATA.subjects;
        }

        const cached = await this.getFromStorage('subjects');
        if (cached) return cached;

        this.requestDataFromBot('get_subjects');
        return [];
    },

    async getGrades(studentId) {
        if (this.isDemoMode()) {
            return DEMO_DATA.grades[studentId] || [];
        }

        const cached = await this.getFromStorage(`grades_${studentId}`);
        if (cached) return cached;

        this.requestDataFromBot('get_grades', { student_id: studentId });
        return [];
    },

    async addGrade(studentId, subjectId, grade, comment) {
        this.sendDataToBot('add_grade', {
            student_id: studentId,
            subject_id: subjectId,
            grade: grade,
            comment: comment
        });
        return true;
    },

    async updateGrade(gradeId, newGrade, comment) {
        this.sendDataToBot('update_grade', {
            grade_id: gradeId,
            grade: newGrade,
            comment: comment
        });
        return true;
    },

    async getHomework() {
        if (this.isDemoMode()) {
            return DEMO_DATA.homework;
        }

        const cached = await this.getFromStorage('homework');
        if (cached) return cached;

        this.requestDataFromBot('get_homework');
        return [];
    },

    async getStatistics(studentId) {
        if (this.isDemoMode()) {
            return DEMO_DATA.statistics[studentId] || {
                overall_average: 0,
                total_grades: 0,
                subject_averages: {}
            };
        }

        const cached = await this.getFromStorage(`stats_${studentId}`);
        if (cached) return cached;

        this.requestDataFromBot('get_statistics', { student_id: studentId });
        return {
            overall_average: 0,
            total_grades: 0,
            subject_averages: {}
        };
    },

    async getParentStudents(parentId) {
        if (this.isDemoMode()) {
            const studentIds = DEMO_DATA.parent_students[parentId] || [];
            return DEMO_DATA.students.filter(s => studentIds.includes(s.student_id));
        }

        const cached = await this.getFromStorage(`parent_students_${parentId}`);
        if (cached) return cached;

        this.requestDataFromBot('get_parent_students', { parent_id: parentId });
        return [];
    },

    // Запрос данных у бота
    requestDataFromBot(action, params = {}) {
        // Закрываем Mini App и отправляем команду боту
        // Бот обработает команду и откроет Mini App заново с данными
        const command = `/${action}`;
        window.Telegram.WebApp.close();
    },

    // Показать уведомление
    showAlert(message) {
        window.Telegram.WebApp.showAlert(message);
    },

    // Показать подтверждение
    async showConfirm(message) {
        return new Promise((resolve) => {
            window.Telegram.WebApp.showConfirm(message, resolve);
        });
    },

    // Показать всплывающее уведомление
    showPopup(message) {
        window.Telegram.WebApp.showPopup({
            message: message
        });
    }
};

// Helper functions
function calculateAverage(grades) {
    if (!grades || grades.length === 0) return 0;
    const sum = grades.reduce((acc, g) => acc + g.grade, 0);
    return (sum / grades.length).toFixed(2);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
}

function isDeadlineUrgent(deadline) {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffDays = (deadlineDate - now) / (1000 * 60 * 60 * 24);
    return diffDays <= 1;
}

// Инициализация при загрузке данных от бота
window.addEventListener('message', (event) => {
    // Получение данных от бота через postMessage
    if (event.data && event.data.type === 'bot_data') {
        const { key, value } = event.data;
        API.saveToStorage(key, value);

        // Перезагрузить интерфейс
        location.reload();
    }
});
