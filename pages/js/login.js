// Encor Login JS Controller

document.addEventListener('DOMContentLoaded', () => {

    const card = document.getElementById('login-card');
    const form = document.getElementById('login-form');

    // Smooth card entrance animation
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 80);
    }

    if (form) {
        form.addEventListener('submit', handleLoginSubmit);
    }
});

async function handleLoginSubmit(e) {
    e.preventDefault();

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errEl = document.getElementById('error-message');
    const card = document.getElementById('login-card');

    if (!usernameInput || !passwordInput) return;

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (errEl) errEl.style.display = 'none';

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (res.ok && data.status === 'success') {
            // Store session token
            localStorage.setItem('encor_token', data.token);
            localStorage.setItem('encor_user', data.username);

            // Card success animation
            if (card) {
                card.style.transition = 'all 0.4s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateY(-20px)';
            }

            const overlay = document.getElementById('page-overlay');
            if (overlay) overlay.classList.add('active');

            setTimeout(() => {
                window.location.href = '/';
            }, 300);
        } else {
            if (errEl) {
                errEl.textContent = data.detail || 'Invalid username or password';
                errEl.style.display = 'block';
            }

            // Card error shake animation
            if (card) {
                card.style.transition = 'transform 0.08s ease';
                let shakes = 0;
                const shakeInterval = setInterval(() => {
                    card.style.transform = shakes % 2 === 0 ? 'translateX(-8px)' : 'translateX(8px)';
                    shakes++;
                    if (shakes > 6) {
                        clearInterval(shakeInterval);
                        card.style.transition = 'transform 0.3s ease';
                        card.style.transform = 'translateX(0)';
                    }
                }, 80);
            }
        }
    } catch (err) {
        console.error('Login error:', err);
        if (errEl) {
            errEl.textContent = 'Unable to connect to Encor authentication service.';
            errEl.style.display = 'block';
        }
    }
}
