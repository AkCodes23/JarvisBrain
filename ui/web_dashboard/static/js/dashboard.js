// Dashboard functionality
document.addEventListener('DOMContentLoaded', () => {
    // Initialize dashboard
    updateStatus();
    updateLogs();
    
    // Set up periodic updates
    setInterval(updateStatus, 5000);  // Update status every 5 seconds
    setInterval(updateLogs, 10000);   // Update logs every 10 seconds
});

// Update system status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update system status
        const systemStatus = document.getElementById('system-status');
        systemStatus.textContent = data.system.status;
        systemStatus.className = `status-value status-${data.system.status.toLowerCase()}`;
        
        // Update components
        const componentsList = document.getElementById('components-list');
        componentsList.innerHTML = '';
        
        for (const [name, component] of Object.entries(data.components)) {
            const card = createComponentCard(name, component);
            componentsList.appendChild(card);
        }
        
    } catch (error) {
        console.error('Failed to update status:', error);
    }
}

// Update system logs
async function updateLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        
        const logsList = document.getElementById('logs-list');
        logsList.innerHTML = '';
        
        for (const log of logs) {
            const entry = createLogEntry(log);
            logsList.appendChild(entry);
        }
        
    } catch (error) {
        console.error('Failed to update logs:', error);
    }
}

// Create component card
function createComponentCard(name, component) {
    const card = document.createElement('div');
    card.className = 'component-card';
    
    const header = document.createElement('div');
    header.className = 'component-header';
    
    const nameSpan = document.createElement('span');
    nameSpan.className = 'component-name';
    nameSpan.textContent = name;
    
    const statusSpan = document.createElement('span');
    statusSpan.className = `component-status status-${component.status.toLowerCase()}`;
    statusSpan.textContent = component.status;
    
    header.appendChild(nameSpan);
    header.appendChild(statusSpan);
    
    const details = document.createElement('div');
    details.className = 'component-details';
    
    for (const [key, value] of Object.entries(component)) {
        if (key !== 'status') {
            const detail = document.createElement('div');
            detail.className = 'component-detail';
            detail.innerHTML = `<strong>${key}:</strong> ${value}`;
            details.appendChild(detail);
        }
    }
    
    card.appendChild(header);
    card.appendChild(details);
    
    return card;
}

// Create log entry
function createLogEntry(log) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    
    const timestamp = document.createElement('span');
    timestamp.className = 'log-timestamp';
    timestamp.textContent = new Date(log.timestamp).toLocaleString();
    
    const level = document.createElement('span');
    level.className = `log-level level-${log.level.toLowerCase()}`;
    level.textContent = log.level;
    
    const message = document.createElement('span');
    message.className = 'log-message';
    message.textContent = log.message;
    
    entry.appendChild(timestamp);
    entry.appendChild(level);
    entry.appendChild(message);
    
    return entry;
} 