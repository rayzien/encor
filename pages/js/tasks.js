// Tasks Page JS

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('launch-task-modal');
    const openBtn = document.getElementById('open-launch-modal-btn');
    const closeBtn = document.getElementById('close-launch-modal-btn');
    const form = document.getElementById('launch-task-form');
    const container = document.getElementById('tasks-container');
    const accountSelect = document.getElementById('task-account-select');

    // Stats
    const statTotal = document.getElementById('stat-total-tasks');
    const statRunning = document.getElementById('stat-running-tasks');
    const statCompleted = document.getElementById('stat-completed-tasks');

    if (openBtn) {
        openBtn.addEventListener('click', async () => {
            await populateAccounts();
            modal.style.display = 'flex';
        });
    }
    if (closeBtn) closeBtn.addEventListener('click', () => modal.style.display = 'none');

    async function populateAccounts() {
        try {
            const res = await fetch('/api/accounts/');
            if (!res.ok) return;
            const accounts = await res.json();
            if (accountSelect) {
                accountSelect.innerHTML = '<option value="">Select Connected Account...</option>' +
                    accounts.map(a => `<option value="${a.id}">@${a.username} (${a.safety_status})</option>`).join('');
            }
        } catch (err) {
            console.error('Error populating account select:', err);
        }
    }

    async function loadTasks() {
        try {
            const res = await fetch('/api/tasks/');
            if (!res.ok) return;
            const tasks = await res.json();
            renderTasks(tasks);
        } catch (err) {
            console.error('Failed to load tasks:', err);
        }
    }

    function renderTasks(tasks) {
        if (!container) return;

        statTotal.textContent = tasks.length;
        statRunning.textContent = tasks.filter(t => t.status === 'running').length;
        statCompleted.textContent = tasks.filter(t => t.status === 'completed').length;

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p class="font-body text-muted">No automation tasks initiated yet. Click 'Launch New Task' to select a targeting workflow.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.map(t => {
            const cfg = JSON.parse(t.config_json || '{}');
            const targetSummary = cfg.tags ? cfg.tags.join(', ') : (cfg.usernames ? cfg.usernames.join(', ') : (cfg.locations ? cfg.locations.join(', ') : 'Default'));
            
            return `
                <div class="task-card card-glow">
                    <div class="task-card-header">
                        <div>
                            <span class="badge font-mono badge-${t.status}">${t.status.toUpperCase()}</span>
                            <h4 class="font-heading task-title">${t.task_type}</h4>
                        </div>
                        <span class="font-mono text-muted">ID: #${t.id}</span>
                    </div>

                    <div class="task-body font-body text-muted">
                        <p>Targets: <strong>${targetSummary}</strong></p>
                        <p>Progress: <strong class="text-amber">${t.progress} / ${t.total_target}</strong> actions completed</p>
                        ${t.log_output ? `<pre class="log-box font-mono">${t.log_output.trim()}</pre>` : ''}
                    </div>

                    <div class="task-card-actions">
                        ${t.status === 'running' ? `<button class="btn-secondary font-accent" onclick="stopTask(${t.id})">Stop Task</button>` : ''}
                        <button class="btn-delete font-accent" onclick="deleteTask(${t.id})">Delete Log</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const accountId = accountSelect.value ? parseInt(accountSelect.value) : null;
            const taskType = document.getElementById('task-type-select').value;
            const rawTargets = document.getElementById('task-targets-input').value;
            const amount = parseInt(document.getElementById('task-amount-input').value) || 10;
            const skipTop = document.getElementById('task-skip-top').checked;
            const randomize = document.getElementById('task-randomize').checked;
            const interact = document.getElementById('task-interact').checked;

            const targetsList = rawTargets.split(',').map(s => s.trim()).filter(Boolean);

            let configObj = {
                amount: amount,
                skip_top_posts: skipTop,
                randomize: randomize,
                interact: interact
            };

            if (taskType.includes('tag')) configObj.tags = targetsList;
            else if (taskType.includes('location')) configObj.locations = targetsList;
            else if (taskType.includes('user') || taskType.includes('list')) configObj.usernames = targetsList;

            try {
                const res = await fetch('/api/tasks/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: accountId,
                        task_type: taskType,
                        config: configObj
                    })
                });

                if (res.ok) {
                    modal.style.display = 'none';
                    form.reset();
                    loadTasks();
                } else {
                    const err = await res.json();
                    alert(err.detail || 'Failed to queue task');
                }
            } catch (err) {
                console.error('Error launching task:', err);
            }
        });
    }

    window.stopTask = async function(id) {
        await fetch(`/api/tasks/${id}/stop`, { method: 'POST' });
        loadTasks();
    };

    window.deleteTask = async function(id) {
        if (confirm('Delete this task entry?')) {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            loadTasks();
        }
    };

    loadTasks();
    setInterval(loadTasks, 5000); // Live refresh every 5s
});
