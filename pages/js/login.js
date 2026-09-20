// GSAP Antigravity Login Logic

document.addEventListener('DOMContentLoaded', () => {
    initGSAP();
    
    const form = document.getElementById('login-form');
    form.addEventListener('submit', handleLogin);
});

function initGSAP() {
    // Smoothly drop in the login card
    gsap.from('.login-card', {
        y: -50,
        opacity: 0,
        duration: 1.2,
        ease: 'power4.out',
        delay: 0.2,
        rotationX: 10,
        transformPerspective: 800
    });

    // Pop in the login button
    gsap.from('.gs-btn', {
        scale: 0.8,
        opacity: 0,
        duration: 0.8,
        ease: 'back.out(1.7)',
        delay: 0.8
    });
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-message');
    
    errorMsg.style.display = 'none';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // Animate card away on success
            gsap.to('.login-card', {
                y: 50,
                opacity: 0,
                duration: 0.6,
                ease: 'power3.in',
                onComplete: () => {
                    // Redirect to dashboard
                    window.location.href = '/';
                }
            });
        } else {
            // Shake animation on error
            errorMsg.textContent = data.detail || 'Login failed';
            errorMsg.style.display = 'block';
            
            gsap.fromTo('.login-card', 
                { x: -10 }, 
                { x: 10, duration: 0.1, yoyo: true, repeat: 5, ease: 'none', onComplete: () => gsap.set('.login-card', {x: 0})}
            );
        }
    } catch (error) {
        errorMsg.textContent = 'Server connection error';
        errorMsg.style.display = 'block';
    }
}
