// Student interface logic

async function initStudentInterface(userId) {
    const studentInterface = document.getElementById('student-interface');
    studentInterface.style.display = 'block';

    const student = await API.getStudent(userId);

    if (!student) {
        document.getElementById('student-stats').innerHTML = '<div class="empty-state"><div class="empty-state-icon">❌</div><div class="empty-state-text">Вы не зарегистрированы как ученик.<br>Обратитесь к учителю.</div></div>';
        return;
    }

    await loadStudentStatistics(student.student_id);
    await loadStudentGradesView(student.student_id);
    await loadStudentHomework();
}

async function loadStudentStatistics(studentId) {
    try {
        const stats = await API.getStatistics(studentId);
        const statsDiv = document.getElementById('student-stats');

        statsDiv.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Общий средний балл</div>
                    <div class="stat-value">${stats.overall_average || 0}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Всего оценок</div>
                    <div class="stat-value">${stats.total_grades || 0}</div>
                </div>
            </div>
        `;

        if (stats.subject_averages && Object.keys(stats.subject_averages).length > 0) {
            const subjectStats = Object.entries(stats.subject_averages)
                .map(([subject, data]) => `<div class="stat-card"><h3>${subject}</h3><div class="stat-value">${data.average}</div><div class="stat-label">${data.count} оценок</div>${data.last_grade ? `<p style="margin-top: 8px; color: #666;">Последняя: <strong>${data.last_grade}</strong></p>` : ''}</div>`).join('');

            statsDiv.innerHTML += `<h3 style="margin-top: 20px; margin-bottom: 12px;">По предметам:</h3><div class="stat-grid">${subjectStats}</div>`;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function loadStudentGradesView(studentId) {
    try {
        const grades = await API.getGrades(studentId);
        const subjects = await API.getSubjects();
        const tbody = document.getElementById('student-grades-tbody');

        tbody.innerHTML = '';

        if (subjects.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="empty-state"><div class="empty-state-icon">📚</div><div class="empty-state-text">Нет данных об оценках</div></td></tr>';
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
                        ${subjectGrades.map(g => `<span class="grade-badge grade-${g.grade}" title="${g.comment || ''} (${formatDate(g.date)})">${g.grade}</span>`).join('') || '<span style="color: #999;">Нет оценок</span>'}
                    </div>
                </td>
                <td><strong>${average || '-'}</strong></td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading grades:', error);
        API.showAlert('Ошибка загрузки оценок');
    }
}

async function loadStudentHomework() {
    try {
        const homework = await API.getHomework();
        const homeworkDiv = document.getElementById('student-homework');

        if (homework.length === 0) {
            homeworkDiv.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-text">Нет домашних заданий</div></div>';
            return;
        }

        homework.sort((a, b) => {
            if (!a.deadline) return 1;
            if (!b.deadline) return -1;
            return new Date(a.deadline) - new Date(b.deadline);
        });

        homeworkDiv.innerHTML = homework.map(hw => `
            <div class="homework-card">
                <h3>📚 ${hw.subject_name}</h3>
                <p><strong>${hw.title}</strong></p>
                <p>${hw.description}</p>
                ${hw.deadline ? `<span class="homework-deadline ${isDeadlineUrgent(hw.deadline) ? 'urgent' : ''}">📅 ${formatDateTime(hw.deadline)}</span>` : ''}
                ${hw.file_id ? '<p>📎 Есть прикрепленный файл</p>' : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading homework:', error);
    }
}
