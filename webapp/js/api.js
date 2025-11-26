// API helper для связи с Backend сервером
// Работает через REST API

// Конфигурация: URL VDS сервера
// Используем текущий origin, так как фронтенд и бэкенд будут на одном адресе (через Cloudflare)
const API_BASE_URL = window.location.origin;

const API = {
    baseUrl: API_BASE_URL, // используем URL VDS сервера

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

    // ============ HTTP REQUEST HELPERS ============

    async apiRequest(method, endpoint, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            const result = await response.json();

            if (!result.success) {
                console.error('API Error:', result.error);
                throw new Error(result.error || 'API request failed');
            }

            return result.data;
        } catch (error) {
            console.error('Request error:', error);
            throw error;
        }
    },

    // ============ STUDENTS ============

    async getStudents() {
        if (this.isDemoMode()) {
            return DEMO_DATA.students;
        }

        return await this.apiRequest('GET', '/api/students');
    },

    async getStudent(studentId) {
        if (this.isDemoMode()) {
            const students = DEMO_DATA.students;
            return students.find(s => s.student_id === studentId);
        }

        return await this.apiRequest('GET', `/api/students/${studentId}`);
    },

    // ============ SUBJECTS ============

    async getSubjects(teacherId = null) {
        if (this.isDemoMode()) {
            return DEMO_DATA.subjects;
        }

        const endpoint = teacherId ? `/api/subjects?teacher_id=${teacherId}` : '/api/subjects';
        return await this.apiRequest('GET', endpoint);
    },

    // ============ GRADES ============

    async getGrades(studentId) {
        if (this.isDemoMode()) {
            return DEMO_DATA.grades[studentId] || [];
        }

        return await this.apiRequest('GET', `/api/grades?student_id=${studentId}`);
    },

    async addGrade(studentId, subjectId, grade, comment = '', teacherId = 1) {
        if (this.isDemoMode()) {
            console.log('Demo mode: Grade not saved');
            return true;
        }

        await this.apiRequest('POST', '/api/grades', {
            student_id: studentId,
            subject_id: subjectId,
            grade: grade,
            comment: comment,
            teacher_id: teacherId,
            date: new Date().toISOString().split('T')[0]
        });

        return true;
    },

    async updateGrade(gradeId, newGrade, comment = '') {
        if (this.isDemoMode()) {
            console.log('Demo mode: Grade not updated');
            return true;
        }

        await this.apiRequest('PUT', `/api/grades/${gradeId}`, {
            grade: newGrade,
            comment: comment
        });

        return true;
    },

    // ============ HOMEWORK ============

    async getHomework(subjectId = null) {
        if (this.isDemoMode()) {
            return DEMO_DATA.homework;
        }

        const endpoint = subjectId ? `/api/homework?subject_id=${subjectId}` : '/api/homework';
        return await this.apiRequest('GET', endpoint);
    },

    // ============ STATISTICS ============

    async getStatistics(studentId) {
        if (this.isDemoMode()) {
            return DEMO_DATA.statistics[studentId] || {
                overall_average: 0,
                total_grades: 0,
                subject_averages: {}
            };
        }

        return await this.apiRequest('GET', `/api/statistics?student_id=${studentId}`);
    },

    // ============ PARENT STUDENTS ============

    async getParentStudents(parentId) {
        if (this.isDemoMode()) {
            const studentIds = DEMO_DATA.parent_students[parentId] || [];
            return DEMO_DATA.students.filter(s => studentIds.includes(s.student_id));
        }

        return await this.apiRequest('GET', `/api/parent/${parentId}/students`);
    },

    // ============ TELEGRAM HELPERS ============

    // Показать уведомление
    showAlert(message) {
        if (this.isTelegramWebApp()) {
            window.Telegram.WebApp.showAlert(message);
        } else {
            alert(message);
        }
    },

    // Показать подтверждение
    async showConfirm(message) {
        if (this.isTelegramWebApp()) {
            return new Promise((resolve) => {
                window.Telegram.WebApp.showConfirm(message, resolve);
            });
        } else {
            return confirm(message);
        }
    },

    // Показать всплывающее уведомление
    showPopup(message) {
        if (this.isTelegramWebApp()) {
            window.Telegram.WebApp.showPopup({
                message: message
            });
        } else {
            alert(message);
        }
    },

    // Закрыть Mini App
    close() {
        if (this.isTelegramWebApp()) {
            window.Telegram.WebApp.close();
        } else {
            console.log('Demo mode: Close not available');
        }
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
