// Encor Master UI Controller — Scroll, Navbar, Transitions, Reveal Animations

document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------
    // 1. Navbar Scroll Effect
    // -----------------------------------------------
    const navbar = document.getElementById('navbar');
    
    function handleScroll() {
        if (window.scrollY > 30) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        triggerReveal();
    }

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial check

    // -----------------------------------------------
    // 2. Burger Menu Logic
    // -----------------------------------------------
    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');

    if (burger && mobileMenu) {
        burger.addEventListener('click', () => {
            burger.classList.toggle('toggle');
            mobileMenu.classList.toggle('active');
        });

        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                burger.classList.remove('toggle');
                mobileMenu.classList.remove('active');
            });
        });
    }

    // -----------------------------------------------
    // 3. Smooth Page Fade Transitions
    // -----------------------------------------------
    const overlay = document.getElementById('page-overlay');
    
    // Fade in on page load
    if (overlay) {
        overlay.classList.remove('active');
    }

    // Attach click handlers to all internal navigation links
    document.querySelectorAll('a[href^="/"], a[href^="http://127.0.0.1"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const targetUrl = link.getAttribute('href');
            
            // Ignore hash links or same-page anchors
            if (!targetUrl || targetUrl.startsWith('#') || targetUrl === window.location.pathname) {
                return;
            }

            e.preventDefault();
            if (overlay) overlay.classList.add('active');
            
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 250);
        });
    });

    // -----------------------------------------------
    // 4. Reveal Animations on Scroll
    // -----------------------------------------------
    function triggerReveal() {
        const reveals = document.querySelectorAll('.reveal');
        const windowHeight = window.innerHeight;
        
        reveals.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            const elementVisible = 100;
            
            if (elementTop < windowHeight - elementVisible) {
                el.classList.add('active');
            }
        });
    }

    triggerReveal(); // Initial trigger
});
