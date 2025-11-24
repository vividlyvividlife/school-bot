// Parent interface logic

async function initParentInterface(userId) {
    const parentInterface = document.getElementById('parent-interface');
    parentInterface.style.display = 'block';

    // Load children
    await loadChildren(userId);

    // Event listeners
    document.getElementById('child-select').addEventListener('change', handleChildChange);
}

async function loadChildren(parentId) {
    try {
        const children = await API.getParentStudents(parentId);
        const select = document.getElementById('child-select');

        select.innerHTML = '<option value="">Выберите ребенка</option>';

        if (children.length === 0) {
            document.getElementById('parent-stats').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">👶</div>
                    <div class="empty-state-text">
                        У вас нет привязанных детей.<br>
                        Используйте команду /link_child в боте.
                    </div>
                </div>
            `;
            return;
        }

        children.forEach(child => {
            const option = document.createElement('option');
            option.value = child.student_id;
            option.textContent = `${child.full_name} (${child.class_name})`;
            select.appendChild(option);
        });

        // Auto-select if only one child
        if (children.length === 1) {
            select.value = children[0].student_id;
            await handleChildChange({ target: select });
        }
    } catch (error) {
        console.error('Error loading children:', error);
        API.showAlert('Ошибка загрузки детей');
    }
}

async function handleChildChange(event) {
    const studentId = event.target.value;

    if (!studentId) {
        document.getElementById('parent-stats').innerHTML = '';
        document.getElementById('parent-grades-tbody').innerHTML = '';
        document.getElementById('parent-homework').innerHTML = '';
        return;
    }

    await loadChildStatistics(studentId);
    await loadChildGrades(studentId);
    await loadHomework();
}

async function loadChildStatistics(studentId) {
    try {
        const stats = await API.getStatistics(studentId);
        const statsDiv = document.getElementById('parent-stats');

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
                .map(([subject, data]) => `
                    <div class="stat-card">
                        <h3>${subject}</h3>
                        <div class="stat-value">${data.average}</div>
                        <div class="stat-label">${data.count} оценок</div>
                    </div>
                `).join('');

            statsDiv.innerHTML += `
                <h3 style="margin-top: 20px; margin-bottom: 12px;">По предметам:</h3>
                <div class="stat-grid">
                    ${subjectStats}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function loadChildGrades(studentId) {
    try {
        const grades = await API.getGrades(studentId);
        const subjects = await API.getSubjects();
        const tbody = document.getElementById('parent-grades-tbody');

        tbody.innerHTML = '';

        if (subjects.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="empty-state">
                        <div class="empty-state-icon">📚</div>
                        <div class="empty-state-text">Нет данных об оценках</div>
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
                            <span class="grade-badge grade-${g.grade}" 
                                  title="${g.comment || ''} (${formatDate(g.date)})">
                                ${g.grade}
                            </span>
                        `).join('') || '<span style="color: #999;">Нет оценок</span>'}
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

async function loadHomework() {
    try {
        const homework = await API.getHomework();
        const homeworkDiv = document.getElementById('parent-homework');

        if (homework.length === 0) {
            homeworkDiv.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <div class="empty-state-text">Нет домашних заданий</div>
                </div>
            `;
            return;
        }

        homeworkDiv.innerHTML = homework.map(hw => `
            <div class="homework-card">
                <h3>📚 ${hw.subject_name}</h3>
                <p><strong>${hw.title}</strong></p>
                <p>${hw.description}</p>
                ${hw.deadline ? `
                    <span class="homework-deadline ${isDeadlineUrgent(hw.deadline) ? 'urgent' : ''}">
                        📅 ${formatDateTime(hw.deadline)}
                    </span>
                ` : ''}
                ${hw.file_id ? '<p>📎 Есть прикрепленный файл</p>' : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading homework:', error);
    }
}
