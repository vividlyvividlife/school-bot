// Teacher interface logic

async function initTeacherInterface(userId) {
    const teacherInterface = document.getElementById('teacher-interface');
    teacherInterface.style.display = 'block';

    // Load students
    await loadStudents();

    // Event listeners
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
            option.textContent = `${student.full_name} (${student.class_name})`;
            select.appendChild(option);
        });

        // Load class statistics
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
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-state">
                        <div class="empty-state-icon">📚</div>
                        <div class="empty-state-text">Нет предметов. Добавьте предметы в боте.</div>
                    </td>
                </tr>
            `;
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
                        ${subjectGrades.map(g => `
                            <span class="grade-badge grade-${g.grade} grade-editable" 
                                  data-grade-id="${g.grade_id}"
                                  data-current-grade="${g.grade}"
                                  title="${g.comment || ''} (${formatDate(g.date)})">
                                ${g.grade}
                            </span>
                        `).join('')}
                        <button class="btn btn-success btn-small" 
                                onclick="addNewGrade(${studentId}, ${subject.subject_id})">
                            + Добавить
                        </button>
                    </div>
                </td>
                <td><strong>${average}</strong></td>
                <td>
                    <button class="btn btn-primary btn-small" 
                            onclick="viewGradeHistory(${studentId}, ${subject.subject_id})">
                        История
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Add click listeners to editable grades
        document.querySelectorAll('.grade-editable').forEach(badge => {
            badge.addEventListener('click', handleGradeEdit);
        });
    } catch (error) {
        console.error('Error loading grades:', error);
        API.showAlert('Ошибка загрузки оценок');
    }
}

async function handleGradeEdit(event) {
    const gradeId = event.target.dataset.gradeId;
    const currentGrade = event.target.dataset.currentGrade;

    const newGrade = prompt(`Текущая оценка: ${currentGrade}\nВведите новую оценку (1-10):`, currentGrade);

    if (!newGrade || newGrade === currentGrade) return;

    const grade = parseInt(newGrade);
    if (isNaN(grade) || grade < 1 || grade > 10) {
        API.showAlert('Оценка должна быть от 1 до 10');
        return;
    }

    const comment = prompt('Комментарий (необязательно):');

    try {
        const success = await API.updateGrade(gradeId, grade, comment);
        if (success) {
            API.showAlert('Оценка обновлена!');
            // Reload grades
            const studentId = document.getElementById('student-select').value;
            await loadStudentGrades(studentId);
        }
    } catch (error) {
        console.error('Error updating grade:', error);
        API.showAlert('Ошибка обновления оценки');
    }
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
        const success = await API.addGrade(studentId, subjectId, gradeValue, comment);
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
    // This would open a modal or new view with grade history
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
