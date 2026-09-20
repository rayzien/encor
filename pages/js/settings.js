// Settings Page JS

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('settings-form');
    const headlessChk = document.getElementById('setting-headless');
    const stealthChk = document.getElementById('setting-stealth');
    const cookiesChk = document.getElementById('setting-cookies');
    const delayMinInput = document.getElementById('setting-delay-min');
    const delayMaxInput = document.getElementById('setting-delay-max');
    const statusMsg = document.getElementById('settings-status-msg');

    async function loadSettings() {
        try {
            const res = await fetch('/api/settings/');
            if (!res.ok) return;
            const data = await res.json();
            
            if (headlessChk) headlessChk.checked = data.headless_mode === 'true';
            if (stealthChk) stealthChk.checked = data.stealth_mode === 'true';
            if (cookiesChk) cookiesChk.checked = data.auto_save_cookies === 'true';
            if (delayMinInput) delayMinInput.value = data.global_delay_min || '3.0';
            if (delayMaxInput) delayMaxInput.value = data.global_delay_max || '8.0';
        } catch (err) {
            console.error('Failed to load settings:', err);
        }
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const payload = {
                headless_mode: headlessChk.checked ? 'true' : 'false',
                stealth_mode: stealthChk.checked ? 'true' : 'false',
                auto_save_cookies: cookiesChk.checked ? 'true' : 'false',
                global_delay_min: delayMinInput.value,
                global_delay_max: delayMaxInput.value
            };

            try {
                const res = await fetch('/api/settings/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    statusMsg.style.display = 'inline';
                    setTimeout(() => statusMsg.style.display = 'none', 3000);
                }
            } catch (err) {
                console.error('Failed to save settings:', err);
            }
        });
    }

    loadSettings();
});
