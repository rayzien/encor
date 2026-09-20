// Encor Dashboard JS

document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------
    // 1. Burger Menu
    // -----------------------------------------------
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    let menuOpen = false;

    if (burger) {
        burger.addEventListener('click', () => {
            menuOpen = !menuOpen;
            burger.classList.toggle('toggle');
            mobileMenu.classList.toggle('active');
        });
    }

    document.querySelectorAll('.mobile-link').forEach(link => {
        link.addEventListener('click', () => {
            if (menuOpen) {
                menuOpen = false;
                burger.classList.remove('toggle');
                mobileMenu.classList.remove('active');
            }
        });
    });

    // -----------------------------------------------
    // 2. Page Transitions
    // -----------------------------------------------
    const overlay = document.getElementById('page-transition');

    document.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href');
            if (overlay) {
                overlay.classList.add('active');
                setTimeout(() => { window.location.href = target; }, 350);
            } else {
                window.location.href = target;
            }
        });
    });

    if (overlay) overlay.classList.remove('active');

    // -----------------------------------------------
    // 3. Reveal on scroll
    // -----------------------------------------------
    function reveal() {
        document.querySelectorAll('.reveal').forEach(el => {
            const top = el.getBoundingClientRect().top;
            if (top < window.innerHeight - 60) {
                el.classList.add('active');
            }
        });
    }

    const scrollTarget = document.getElementById('scroll-container') || window;
    if (scrollTarget.addEventListener) {
        scrollTarget.addEventListener('scroll', reveal);
    }
    reveal();

    // Stagger reveals for a cascade effect
    document.querySelectorAll('.reveal').forEach((el, i) => {
        el.style.transitionDelay = (i * 0.08) + 's';
    });

    // -----------------------------------------------
    // 4. Master Toggle
    // -----------------------------------------------
    const masterToggle = document.getElementById('master-toggle');
    const toggleLabel = document.getElementById('toggle-label');

    if (masterToggle && toggleLabel) {
        masterToggle.addEventListener('change', () => {
            if (masterToggle.checked) {
                toggleLabel.textContent = 'Engine active. Accounts will be processed.';
                toggleLabel.style.color = '#22c55e';
            } else {
                toggleLabel.textContent = 'All systems stopped. Toggle to begin.';
                toggleLabel.style.color = '';
            }
        });
    }

    // -----------------------------------------------
    // 5. Account Toggles
    // -----------------------------------------------
    const accountToggles = document.querySelectorAll('.account-toggle');
    const runningEl = document.getElementById('running-count');

    function updateRunning() {
        if (!runningEl) return;
        let count = 0;
        accountToggles.forEach(t => { if (t.checked) count++; });
        runningEl.textContent = count;
    }

    accountToggles.forEach(t => t.addEventListener('change', updateRunning));
    updateRunning();

    // -----------------------------------------------
    // 6. Health Check
    // -----------------------------------------------
    checkHealth();
});

async function checkHealth() {
    const badgeEl = document.getElementById('engine-badge');
    const statusEl = document.getElementById('engine-status');
    try {
        const res = await fetch('/api/health');
        const data = await res.json();
        if (data.status === 'ok') {
            console.log('[encor] backend online');
            if (statusEl) statusEl.textContent = 'Online';
            if (badgeEl) {
                badgeEl.innerHTML = '<span class="status-dot dot-green"></span><span class="font-space">Engine Online</span>';
            }
        }
    } catch (err) {
        console.warn('[encor] backend unreachable');
        if (statusEl) statusEl.textContent = 'Offline';
        if (badgeEl) {
            badgeEl.innerHTML = '<span class="status-dot dot-red"></span><span class="font-space">Offline</span>';
            badgeEl.style.background = 'rgba(239,68,68,0.1)';
            badgeEl.style.borderColor = 'rgba(239,68,68,0.2)';
            badgeEl.style.color = '#ef4444';
        }
    }
}
