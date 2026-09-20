// Encor Login JS — GSAP animations + API auth

document.addEventListener('DOMContentLoaded', () => {
    // Animate login card entrance
    gsap.from('#login-card', {
        y: -50,
        opacity: 0,
        duration: 1.2,
        ease: 'power4.out',
        delay: 0.2,
        rotationX: 10,
        transformPerspective: 800
    });

    // Burger menu
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    if (burger && mobileMenu) {
        burger.addEventListener('click', () => {
            burger.classList.toggle('toggle');
            mobileMenu.classList.toggle('active');
        });
    }

    // Login form
    const form = document.getElementById('login-form');
    form.addEventListener('submit', handleLogin);
});

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-message');
    
    errorMsg.style.display = 'none';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            gsap.to('#login-card', {
                y: 50,
                opacity: 0,
                duration: 0.6,
                ease: 'power3.in',
                onComplete: () => { window.location.href = '/'; }
            });
        } else {
            errorMsg.textContent = data.detail || 'Login failed';
            errorMsg.style.display = 'block';
            
            gsap.fromTo('#login-card', 
                { x: -10 }, 
                { x: 10, duration: 0.1, yoyo: true, repeat: 5, ease: 'none',
                  onComplete: () => gsap.set('#login-card', { x: 0 }) }
            );
        }
    } catch (error) {
        errorMsg.textContent = 'Server connection error';
        errorMsg.style.display = 'block';
    }
}
