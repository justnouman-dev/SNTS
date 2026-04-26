// Main JavaScript utilities for SNTS

// Global utility functions
function showNotification(message, type = 'info') {
    // Simple notification system
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Format date/time
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Hydration reminder system
function checkHydrationReminder() {
    const lastReminder = localStorage.getItem('lastHydrationReminder');
    const now = Date.now();
    const hourInMs = 60 * 60 * 1000;

    if (!lastReminder || (now - parseInt(lastReminder)) > hourInMs) {
        if (Notification.permission === 'granted') {
            new Notification('💧 Hydration Reminder', {
                body: 'Time to drink water! Stay hydrated.',
                icon: '/static/images/water.png'
            });
        }
        localStorage.setItem('lastHydrationReminder', now.toString());
    }
}

// Request notification permission
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Initialize hydration reminders
if ('Notification' in window) {
    requestNotificationPermission();
    // Check every hour
    setInterval(checkHydrationReminder, 60 * 60 * 1000);
}

// Export for use in other scripts
window.SNTSUtils = {
    showNotification,
    formatDate,
    formatTime,
    checkHydrationReminder
};
