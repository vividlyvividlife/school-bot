// Teacher interface logic

async function initTeacherInterface(userId) {
    const teacherInterface = document.getElementById('teacher-interface');
    teacherInterface.style.display = 'block';

    window.currentTeacherId = userId;

    await loadStudents();

    document.getElementById('student-select').addEventListener('change', handleStudentChange);
    document.getElementById('add-student-btn').addEventListener('click', handleAddStudent);
}

async function loadStudents() {
    try {
        const students = await API.getStudents();
        const select = document.getElementById('student-select');

        select.innerHTML = '<option value="">Выберите ученика</option>';

        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.student_id;
            option.textContent = `${student.full_name} (${student.class_name || 'Не указан'})`;
            select.appendChild(option);
        });

        await loadClassStatistics();
    } catch (error) {
        console.error('Error loading students:', error);
        API.showAlert('Ошибка загрузки учеников');
    }
}

async function handleStudentChange(event) {
    const studentId = event.target.value;

    if (!studentId) {
        document.getElementById('grades-tbody').innerHTML = '';
        return;
    }

    await loadStudentGrades(studentId);
}

async function loadStudentGrades(studentId) {
    try {
        const grades = await API.getGrades(studentId);
        const subjects = await API.getSubjects();
        const tbody = document.getElementById('grades-tbody');

        tbody.innerHTML = '';

        if (subjects.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-state"><div class="empty-state-icon">📚</div><div class="empty-state-text">Нет предметов.</div></td></tr>';
            return;
        }

        subjects.forEach(subject => {
            const subjectGrades = grades.filter(g => g.subject_id === subject.subject_id);
            const average = calculateAverage(subjectGrades);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${subject.name}</strong></td>
                <td>
                    <div class="grades-list">
                        ${subjectGrades.map(g => `<span class="grade-badge grade-${g.grade} grade-editable" data-grade-id="${g.grade_id}" data-current-grade="${g.grade}" title="${g.comment || ''} (${formatDate(g.date)})">${g.grade}</span>`).join('')}
                        <button class="btn btn-success btn-small" onclick="addNewGrade(${studentId}, ${subject.subject_id})">+ Добавить</button>
                    </div>
                </td>
                <td><strong>${average}</strong></td>
                <td><button class="btn btn-primary btn-small" onclick="viewGradeHistory(${studentId}, ${subject.subject_id})">История</button></td>
            `;
            tbody.appendChild(row);
        });

        document.querySelectorAll('.grade-editable').forEach(badge => {
            badge.addEventListener('click', handleGradeEdit);
        });
    } catch (error) {
        console.error('Error loading grades:', error);
        API.showAlert('Ошибка загрузки оценок');
    }
}

const modal = document.getElementById('edit-grade-modal');
const closeBtn = document.querySelector('.close-modal');
const cancelBtn = document.getElementById('cancel-edit-btn');
const form = document.getElementById('edit-grade-form');

if (closeBtn) closeBtn.onclick = () => modal.style.display = 'none';
if (cancelBtn) cancelBtn.onclick = () => modal.style.display = 'none';
window.onclick = (event) => {
    if (event.target == modal) modal.style.display = 'none';
}

if (form) {
    form.onsubmit = async (e) => {
        e.preventDefault();
        const gradeId = document.getElementById('edit-grade-id').value;
        const grade = parseInt(document.getElementById('edit-grade-value').value);
        const comment = document.getElementById('edit-grade-comment').value;

        if (isNaN(grade) || grade < 1 || grade > 10) {
            API.showAlert('Оценка должна быть от 1 до 10');
            return;
        }

        try {
            const success = await API.updateGrade(gradeId, grade, comment);
            if (success) {
                modal.style.display = 'none';
                API.showAlert('Оценка обновлена!');
                const studentId = document.getElementById('student-select').value;
                await loadStudentGrades(studentId);
            }
        } catch (error) {
            console.error('Error updating grade:', error);
            API.showAlert('Ошибка обновления оценки');
        }
    };
}

function handleGradeEdit(event) {
    const gradeId = event.target.dataset.gradeId;
    const currentGrade = event.target.dataset.currentGrade;
    const currentComment = event.target.title ? event.target.title.split(' (')[0] : '';

    document.getElementById('edit-grade-id').value = gradeId;
    document.getElementById('edit-grade-value').value = currentGrade;
    document.getElementById('edit-grade-comment').value = currentComment;

    modal.style.display = 'block';
}

async function addNewGrade(studentId, subjectId) {
    const grade = prompt('Введите оценку (1-10):');
    if (!grade) return;

    const gradeValue = parseInt(grade);
    if (isNaN(gradeValue) || gradeValue < 1 || gradeValue > 10) {
        API.showAlert('Оценка должна быть от 1 до 10');
        return;
    }

    const comment = prompt('Комментарий (необязательно):');

    try {
        const teacherId = window.currentTeacherId || 1;
        const success = await API.addGrade(studentId, subjectId, gradeValue, comment, teacherId);
        if (success) {
            API.showAlert('Оценка добавлена!');
            await loadStudentGrades(studentId);
        }
    } catch (error) {
        console.error('Error adding grade:', error);
        API.showAlert('Ошибка добавления оценки');
    }
}

function viewGradeHistory(studentId, subjectId) {
    API.showAlert('Функция истории оценок в разработке');
}

function handleAddStudent() {
    API.showAlert('Используйте команду /add_student в боте для добавления ученика');
}

async function loadClassStatistics() {
    try {
        const students = await API.getStudents();
        const statsDiv = document.getElementById('teacher-stats');

        if (students.length === 0) {
            statsDiv.innerHTML = '<p>Нет данных для статистики</p>';
            return;
        }

        let totalAverage = 0;
        let studentCount = 0;

        for (const student of students) {
            const stats = await API.getStatistics(student.student_id);
            if (stats.overall_average > 0) {
                totalAverage += parseFloat(stats.overall_average);
                studentCount++;
            }
        }

        const classAverage = studentCount > 0 ? (totalAverage / studentCount).toFixed(2) : 0;

        statsDiv.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Учеников в классе</div>
                    <div class="stat-value">${students.length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Средний балл класса</div>
                    <div class="stat-value">${classAverage}</div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const addSubjectBtn = document.getElementById('add-subject-btn');
    const addStudentBtn = document.getElementById('add-student-btn');
    const addHomeworkBtn = document.getElementById('add-homework-btn');

    if (addSubjectBtn) {
        addSubjectBtn.addEventListener('click', () => openModal('add-subject-modal'));
    }

    if (addStudentBtn) {
        addStudentBtn.addEventListener('click', () => openModal('add-student-modal'));
    }

    if (addHomeworkBtn) {
        addHomeworkBtn.addEventListener('click', async () => {
            await loadSubjectsForHomework();
            openModal('add-homework-modal');
        });
    }

    document.querySelectorAll('.close-modal').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modalId = e.target.getAttribute('data-modal');
            if (modalId) {
                closeModal(modalId);
            } else {
                const modal = e.target.closest('.modal');
                if (modal) modal.style.display = 'none';
            }
        });
    });

    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modalId = e.target.getAttribute('data-close-modal');
            closeModal(modalId);
        });
    });

    const addSubjectForm = document.getElementById('add-subject-form');
    if (addSubjectForm) {
        addSubjectForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('subject-name').value;
            const maxGrade = parseInt(document.getElementById('subject-max-grade').value);

            try {
                await API.addSubject(name, window.currentTeacherId, maxGrade);
                API.showAlert(`Предмет "${name}" добавлен!`);
                closeModal('add-subject-modal');
                addSubjectForm.reset();
            } catch (error) {
                console.error('Error adding subject:', error);
                API.showAlert('Ошибка при добавлении предмета');
            }
        });
    }

    const addStudentForm = document.getElementById('add-student-form');
    if (addStudentForm) {
        addStudentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('student-full-name').value;
            const className = document.getElementById('student-class').value;

            try {
                await API.addStudent(fullName, className);
                API.showAlert(`Ученик "${fullName}" добавлен!`);
                closeModal('add-student-modal');
                addStudentForm.reset();
                await loadStudents();
            } catch (error) {
                console.error('Error adding student:', error);
                API.showAlert('Ошибка при добавлении ученика');
            }
        });
    }

    const addHomeworkForm = document.getElementById('add-homework-form');
    if (addHomeworkForm) {
        addHomeworkForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const subjectId = parseInt(document.getElementById('homework-subject').value);
            const title = document.getElementById('homework-title').value;
            const description = document.getElementById('homework-description').value;
            const deadline = document.getElementById('homework-deadline').value;

            const formattedDeadline = deadline ? new Date(deadline).toISOString().replace('T', ' ').slice(0, 19) : null;

            try {
                await API.addHomework(subjectId, title, description, window.currentTeacherId, formattedDeadline);
                API.showAlert(`ДЗ "${title}" создано!`);
                closeModal('add-homework-modal');
                addHomeworkForm.reset();
            } catch (error) {
                console.error('Error adding homework:', error);
                API.showAlert('Ошибка при создании ДЗ');
            }
        });
    }
});

async function loadSubjectsForHomework() {
    try {
        const subjects = await API.getSubjects();
        const select = document.getElementById('homework-subject');
        select.innerHTML = '<option value="">Выберите предмет</option>';

        subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.subject_id;
            option.textContent = subject.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading subjects for homework:', error);
    }
}
