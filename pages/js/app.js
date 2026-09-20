// Encor App JS — Dashboard logic + Navigation transitions

document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------
    // 1. Navbar Scroll Effect
    // -----------------------------------------------
    const scrollContainer = document.getElementById('scroll-container');
    const navbar = document.getElementById('navbar');

    if (scrollContainer && navbar) {
        scrollContainer.addEventListener('scroll', () => {
            if (scrollContainer.scrollTop > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            reveal();
        });
    }

    // -----------------------------------------------
    // 2. Burger Menu Logic
    // -----------------------------------------------
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    let isMenuOpen = false;

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
        if (burger) burger.classList.toggle('toggle');
        if (mobileMenu) mobileMenu.classList.toggle('active');
        if (scrollContainer) {
            scrollContainer.style.overflowY = isMenuOpen ? 'hidden' : 'auto';
        }
    }

    if (burger) {
        burger.addEventListener('click', toggleMenu);
    }

    // Close mobile menu on link click
    document.querySelectorAll('.mobile-link').forEach(link => {
        link.addEventListener('click', () => {
            if (isMenuOpen) toggleMenu();
        });
    });

    // -----------------------------------------------
    // 3. Page Transitions (smooth fade on nav)
    // -----------------------------------------------
    const transitionOverlay = document.getElementById('page-transition');
    const pageLinks = document.querySelectorAll('.page-link');

    pageLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href');

            if (transitionOverlay) {
                transitionOverlay.classList.add('active');
                setTimeout(() => {
                    window.location.href = target;
                }, 400);
            } else {
                window.location.href = target;
            }
        });
    });

    // Fade in on page load
    if (transitionOverlay) {
        transitionOverlay.classList.remove('active');
    }

    // -----------------------------------------------
    // 4. Scroll Reveal Animation
    // -----------------------------------------------
    function reveal() {
        const reveals = document.querySelectorAll('.reveal');
        const windowHeight = window.innerHeight;

        reveals.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            if (elementTop < windowHeight - 100) {
                el.classList.add('active');
            }
        });
    }

    reveal();

    // -----------------------------------------------
    // 5. Master Toggle Logic
    // -----------------------------------------------
    const masterToggle = document.getElementById('master-toggle');
    const toggleLabel = document.getElementById('toggle-label');

    if (masterToggle && toggleLabel) {
        masterToggle.addEventListener('change', () => {
            if (masterToggle.checked) {
                toggleLabel.textContent = 'Engine running — all active accounts engaged';
                toggleLabel.style.color = '#22c55e';
            } else {
                toggleLabel.textContent = 'All systems stopped';
                toggleLabel.style.color = '#9ca3af';
            }
        });
    }

    // -----------------------------------------------
    // 6. Account Toggle Logic
    // -----------------------------------------------
    const accountToggles = document.querySelectorAll('.account-toggle');
    const runningCount = document.getElementById('running-count');
    
    function updateRunningCount() {
        if (!runningCount) return;
        let count = 0;
        accountToggles.forEach(t => { if (t.checked) count++; });
        runningCount.textContent = count;
    }

    accountToggles.forEach(toggle => {
        toggle.addEventListener('change', updateRunningCount);
    });

    updateRunningCount();

    // -----------------------------------------------
    // 7. Backend Health Check
    // -----------------------------------------------
    checkHealth();
});


// Backend API
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        if (data.status === 'ok') {
            console.log('✅ Encor Backend Online: ' + data.message);
        }
    } catch (error) {
        console.error('❌ Connection error: Could not reach backend.');
        const statusEl = document.getElementById('engine-status');
        if (statusEl) {
            statusEl.innerHTML = '<span class="status-dot dot-red"></span> Offline';
        }
    }
}

async function launchTask() {
    try {
        const response = await fetch('/api/automation/start', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'ok') {
            alert('✅ Task queued! ID: ' + data.task_id);
        }
    } catch (error) {
        alert('❌ Failed to start task.');
    }
}
