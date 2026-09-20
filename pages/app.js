// Encor Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
});

async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'ok') {
            document.getElementById('backend-status').textContent = 'Backend Online - Efficient Mode';
            addLog(`System check: ${data.message}`);
        } else {
            document.getElementById('backend-status').textContent = 'Backend Issue';
            document.querySelector('.dot').style.backgroundColor = '#e41e3f'; // Red
        }
    } catch (error) {
        document.getElementById('backend-status').textContent = 'Backend Offline';
        document.querySelector('.dot').style.backgroundColor = '#e41e3f'; // Red
        addLog(`Connection error: Could not reach backend.`);
    }
}

function startAutomation() {
    addLog(`Initiating Playwright automation sequence...`);
    // Future API call to backend to start tasks
    setTimeout(() => {
        addLog(`Automation task queued successfully.`);
    }, 500);
}

function addLog(message) {
    const logsContainer = document.getElementById('logs-container');
    const timestamp = new Date().toLocaleTimeString();
    
    // Clear initial "Waiting for events..." text if it's the first log
    if (logsContainer.children.length === 1 && logsContainer.children[0].textContent === 'Waiting for events...') {
        logsContainer.innerHTML = '';
    }
    
    const logElement = document.createElement('p');
    logElement.className = 'log-entry';
    logElement.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
    
    logsContainer.prepend(logElement);
}
