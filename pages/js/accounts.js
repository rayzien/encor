// Accounts Page JS

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('add-account-modal');
    const openBtn = document.getElementById('open-add-modal-btn');
    const closeBtn = document.getElementById('close-modal-btn');
    const form = document.getElementById('add-account-form');
    const container = document.getElementById('accounts-container');
    const emptyState = document.getElementById('accounts-empty-state');

    // Stats elements
    const statTotal = document.getElementById('stat-total-accounts');
    const statActive = document.getElementById('stat-active-accounts');
    const statSafe = document.getElementById('stat-safe-accounts');

    if (openBtn) openBtn.addEventListener('click', () => modal.style.display = 'flex');
    if (closeBtn) closeBtn.addEventListener('click', () => modal.style.display = 'none');

    async function loadAccounts() {
        try {
            const res = await fetch('/api/accounts/');
            if (!res.ok) return;
            const accounts = await res.json();
            renderAccounts(accounts);
        } catch (err) {
            console.error('Failed to load accounts:', err);
        }
    }

    function renderAccounts(accounts) {
        if (!container) return;

        statTotal.textContent = accounts.length;
        statActive.textContent = accounts.filter(a => a.is_active).length;
        statSafe.textContent = accounts.filter(a => a.safety_status === 'safe').length;

        if (accounts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p class="font-body text-muted">No Instagram accounts connected yet. Click 'Add New Account' to get started.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = accounts.map(acc => `
            <div class="account-card card-glow">
                <div class="account-card-header">
                    <div class="account-info">
                        <span class="account-status-dot dot-${acc.safety_status || 'safe'}"></span>
                        <span class="font-heading account-name">@${acc.username}</span>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" class="acc-toggle-check" data-id="${acc.id}" ${acc.is_active ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                <div class="account-details font-body">
                    <p class="text-muted">Safety Status: <strong class="text-${acc.safety_status === 'safe' ? 'green' : 'amber'}">${(acc.safety_status || 'safe').toUpperCase()}</strong></p>
                    <p class="text-muted">Daily Limits: <strong>${acc.daily_likes_limit || 100} Likes / ${acc.daily_follows_limit || 50} Follows</strong></p>
                </div>
                <div class="account-card-actions">
                    <button class="btn-delete font-accent" onclick="deleteAccount(${acc.id})">Delete</button>
                </div>
            </div>
        `).join('');

        // Attach toggle event listeners
        document.querySelectorAll('.acc-toggle-check').forEach(chk => {
            chk.addEventListener('change', async (e) => {
                const id = e.target.dataset.id;
                await fetch(`/api/accounts/${id}/toggle`, { method: 'POST' });
                loadAccounts();
            });
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('acc-username').value;
            const password = document.getElementById('acc-password').value;
            const likesLimit = parseInt(document.getElementById('acc-likes-limit').value) || 100;
            const followsLimit = parseInt(document.getElementById('acc-follows-limit').value) || 50;

            try {
                const res = await fetch('/api/accounts/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username,
                        password,
                        daily_likes_limit: likesLimit,
                        daily_follows_limit: followsLimit
                    })
                });

                if (res.ok) {
                    modal.style.display = 'none';
                    form.reset();
                    loadAccounts();
                } else {
                    const err = await res.json();
                    alert(err.detail || 'Failed to add account');
                }
            } catch (err) {
                console.error('Error creating account:', err);
            }
        });
    }

    window.deleteAccount = async function(id) {
        if (confirm('Are you sure you want to remove this account?')) {
            await fetch(`/api/accounts/${id}`, { method: 'DELETE' });
            loadAccounts();
        }
    };

    loadAccounts();
});
