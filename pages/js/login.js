// Encor Login JS

document.addEventListener('DOMContentLoaded', () => {

    const card = document.getElementById('login-card');

    // Entrance animation
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    }

    // Burger menu
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    if (burger && mobileMenu) {
        burger.addEventListener('click', () => {
            burger.classList.toggle('toggle');
            mobileMenu.classList.toggle('active');
        });
    }

    // Page transitions
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

    // Login form
    const form = document.getElementById('login-form');
    if (form) form.addEventListener('submit', handleLogin);
});

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errEl = document.getElementById('error-message');
    const card = document.getElementById('login-card');
    
    errEl.style.display = 'none';
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        
        if (res.ok && data.status === 'success') {
            // Success animation then redirect
            card.style.transition = 'all 0.4s ease';
            card.style.opacity = '0';
            card.style.transform = 'translateY(-20px)';
            setTimeout(() => { window.location.href = '/'; }, 400);
        } else {
            errEl.textContent = data.detail || 'Invalid credentials';
            errEl.style.display = 'block';
            
            // Shake animation
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
    } catch (err) {
        errEl.textContent = 'Server connection error';
        errEl.style.display = 'block';
    }
}
