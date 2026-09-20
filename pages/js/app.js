// Encor App JS — Matches reference parallax_adventure_website.html logic

document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------
    // 1. Navbar Scroll Effect
    // We listen on the parallax-wrapper, NOT window,
    // because that's where the scroll actually happens.
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

            // Trigger reveal animations on scroll
            reveal();
        });
    }

    // -----------------------------------------------
    // 2. Burger Menu Logic
    // -----------------------------------------------
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');
    let isMenuOpen = false;

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
        burger.classList.toggle('toggle');
        mobileMenu.classList.toggle('active');

        if (scrollContainer) {
            scrollContainer.style.overflowY = isMenuOpen ? 'hidden' : 'auto';
        }
    }

    if (burger) {
        burger.addEventListener('click', toggleMenu);
    }

    // Close mobile menu when a link is clicked
    mobileLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            toggleMenu();

            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                setTimeout(() => {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }, 400);
            }
        });
    });

    // Handle Desktop Links smooth scroll
    const desktopLinks = document.querySelectorAll('.nav-links a');
    desktopLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // -----------------------------------------------
    // 3. Scroll Reveal Animation
    // -----------------------------------------------
    function reveal() {
        const reveals = document.querySelectorAll('.reveal');
        const windowHeight = window.innerHeight;

        reveals.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            const revealPoint = 100;

            if (elementTop < windowHeight - revealPoint) {
                el.classList.add('active');
            }
        });
    }

    // Trigger once on load
    reveal();

    // -----------------------------------------------
    // 4. Backend Health Check
    // -----------------------------------------------
    checkHealth();
});


// -----------------------------------------------
// Backend API Functions
// -----------------------------------------------
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        if (data.status === 'ok') {
            console.log('✅ Encor Backend Online: ' + data.message);
        } else {
            console.warn('⚠️ Backend Issue detected.');
        }
    } catch (error) {
        console.error('❌ Connection error: Could not reach backend.');
    }
}

async function launchTask() {
    console.log('🚀 Initiating Playwright automation sequence...');
    try {
        const response = await fetch('/api/automation/start', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'ok') {
            alert('✅ Automation task queued successfully! Task ID: ' + data.task_id);
        }
    } catch (error) {
        alert('❌ Failed to start automation task.');
    }
}
