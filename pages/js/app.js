// GSAP Antigravity & Parallax Logic

document.addEventListener('DOMContentLoaded', () => {
    initGSAP();
    checkHealth();
});

function initGSAP() {
    gsap.registerPlugin(ScrollTrigger);

    // 1. Parallax Scroll Effect
    // Move the sun down slightly as we scroll
    gsap.to('.layer-sun', {
        yPercent: 30,
        ease: 'none',
        scrollTrigger: {
            trigger: 'body',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        }
    });

    // Move mountains at different speeds (depth illusion)
    gsap.to('.layer-mountain-3', {
        yPercent: 15,
        ease: 'none',
        scrollTrigger: { trigger: 'body', start: 'top top', end: 'bottom top', scrub: true }
    });
    
    gsap.to('.layer-mountain-2', {
        yPercent: 10,
        ease: 'none',
        scrollTrigger: { trigger: 'body', start: 'top top', end: 'bottom top', scrub: true }
    });

    gsap.to('.layer-mountain-1', {
        yPercent: 5,
        ease: 'none',
        scrollTrigger: { trigger: 'body', start: 'top top', end: 'bottom top', scrub: true }
    });
    
    // Foreground stays mostly static, or moves slightly negative
    gsap.to('.layer-foreground', {
        yPercent: 0,
        ease: 'none',
        scrollTrigger: { trigger: 'body', start: 'top top', end: 'bottom top', scrub: true }
    });


    // 2. Antigravity Staggered Entrance Animations
    
    // Sidebar slides in from left
    gsap.from('.sidebar', {
        x: -50,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        delay: 0.2
    });

    // Header drops in
    gsap.from('.top-header', {
        y: -30,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        delay: 0.4
    });

    // Dashboard cards stagger in from bottom with slight 3D rotation
    gsap.from('.gs-card', {
        y: 50,
        rotationX: 15, // Slight 3D tilt
        opacity: 0,
        duration: 1.2,
        stagger: 0.15, // Domino effect
        ease: 'power4.out',
        delay: 0.6,
        transformPerspective: 800
    });
    
    // Animate panels cascading in
    gsap.from('.glass-panel', {
        y: 50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: 'power3.out',
        delay: 0.5,
        rotationX: 15,
        transformPerspective: 800
    });
}

// -----------------------------------------
// Navigation & Burger Menu Logic
// -----------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar Scroll Effect
    const scrollContainer = document.getElementById('scroll-container');
    const navbar = document.getElementById('navbar');

    if (scrollContainer && navbar) {
        scrollContainer.addEventListener('scroll', () => {
            if (scrollContainer.scrollTop > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // 2. Burger Menu Logic
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');
    let isMenuOpen = false;

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
        if(burger) burger.classList.toggle('toggle');
        if(mobileMenu) mobileMenu.classList.toggle('active');
        
        if(scrollContainer) {
            if(isMenuOpen) {
                scrollContainer.style.overflowY = 'hidden';
            } else {
                scrollContainer.style.overflowY = 'auto';
            }
        }
    }

    if (burger) {
        burger.addEventListener('click', toggleMenu);
    }

    mobileLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            toggleMenu();
        });
    });
});


// Backend Logic
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'ok') {
            console.log('System check: ' + data.message);
        } else {
            console.warn('Backend Issue detected.');
        }
    } catch (error) {
        console.error('Connection error: Could not reach backend.');
    }
}

async function launchTask() {
    console.log('Initiating Playwright automation sequence...');
    try {
        const response = await fetch('/api/automation/start', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'ok') {
            alert('Automation task queued successfully! Task ID: ' + data.task_id);
        }
    } catch (error) {
        alert('Failed to start automation task.');
    }
}
