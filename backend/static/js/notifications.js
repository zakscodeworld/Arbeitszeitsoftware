/**
 * Notifications System for BBQ GmbH Zeiterfassung
 * Handles browser notifications with witty messages for work hour alerts
 */

// Container for all notifications
let notificationContainer;

// Array of witty messages for overwork notifications
const overworkMessages = [
    "Zeit zum Feierabend! Dein Laptop wird dich nicht vermissen.",
    "Die Arbeit läuft nicht weg... aber deine Freizeit schon!",
    "Genug für heute! Die Welt rettest du morgen weiter.",
    "Vielleicht solltest du jetzt nach Hause gehen. Deine Pflanze braucht Wasser... und Gesellschaft!",
    "Die Arbeit wird nicht eifersüchtig, wenn du jetzt Freizeit hast.",
    "Hey Workaholic, dein Sofa vermisst dich!",
    "Freizeit ist kein Luxus, sondern eine Notwendigkeit!",
    "8 Stunden sind genug! Gib deinen Augen eine Pause vom Bildschirm.",
    "Feierabend ist nicht nur ein schönes Wort, sondern auch eine gute Idee!",
    "Hast du schon überlegt, was du mit deiner Freizeit anfangen könntest?",
    "Denk daran: Niemand sagt auf dem Sterbebett 'Ich wünschte, ich hätte mehr gearbeitet'!",
    "Deine Netflix-Watchlist weint vor Einsamkeit.",
    "Es ist wissenschaftlich erwiesen, dass zu viel Arbeit unlustig macht.",
    "Zuviel arbeiten ist auch eine Form von Faulheit - nämlich die Faulheit, mit der Arbeit aufzuhören!",
    "Dein Bett fragt sich, wo du so lange bleibst."
];

/**
 * Initialize the notification system
 */
function initNotificationSystem() {
    // Add the CSS for notifications if not already present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                max-width: 350px;
                z-index: 10000;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .notification {
                background-color: #e3f2fd;
                color: #004a99;
                border-left: 4px solid #004a99;
                border-radius: 4px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                margin-bottom: 10px;
                padding: 15px;
                display: flex;
                align-items: flex-start;
                animation: slide-in 0.3s ease-out forwards;
                overflow: hidden;
                max-height: 200px;
                transition: all 0.5s ease;
            }
            
            .notification.closing {
                max-height: 0;
                margin-bottom: 0;
                padding-top: 0;
                padding-bottom: 0;
                opacity: 0;
            }
            
            .notification-icon {
                font-size: 22px;
                margin-right: 12px;
                color: #004a99;
            }
            
            .notification-content {
                flex: 1;
            }
            
            .notification-title {
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 16px;
            }
            
            .notification-message {
                font-size: 14px;
                line-height: 1.4;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: #004a99;
                cursor: pointer;
                font-size: 16px;
                opacity: 0.7;
                padding: 0;
                margin-left: 10px;
                transition: opacity 0.2s;
            }
            
            .notification-close:hover {
                opacity: 1;
            }
            
            @keyframes slide-in {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Create notification container if it doesn't exist
    if (!document.querySelector('.notification-container')) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    } else {
        notificationContainer = document.querySelector('.notification-container');
    }
}

/**
 * Show a browser notification with bell icon
 * Ensures only one notification is displayed at a time
 * @param {string} title - The notification title
 * @param {string} message - The notification message
 * @param {number} duration - How long to show the notification (ms)
 */
function showNotification(title, message, duration = 8000) {
    // Ensure container exists
    if (!notificationContainer) {
        initNotificationSystem();
    }
    
    // Clear any existing notifications first
    clearAllNotifications();
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.id = 'bbq-notification';
    
    // Create HTML structure directly
    notification.innerHTML = `
        <div class="notification-icon">🔔</div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" aria-label="Schließen">×</button>
    `;
    
    // Add close functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        closeNotification(notification);
    });
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            closeNotification(notification);
        }, duration);
    }
    
    return notification;
}

/**
 * Closes a notification with animation
 * @param {HTMLElement} notification - The notification element to close
 */
function closeNotification(notification) {
    if (!notification || !notification.parentNode) return;
    
    notification.classList.add('closing');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 500);
}

/**
 * Clears all existing notifications
 */
function clearAllNotifications() {
    if (!notificationContainer) return;
    
    const existingNotifications = notificationContainer.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        closeNotification(notification);
    });
}

/**
 * Show overwork notification with random witty message
 * @param {number} hours - Number of hours worked
 */
function showOverworkNotification(hours) {
    const randomIndex = Math.floor(Math.random() * overworkMessages.length);
    const message = overworkMessages[randomIndex];
    
    return showNotification(
        `Du hast ${hours.toFixed(1)} Stunden gearbeitet!`,
        message,
        10000 // Show for 10 seconds
    );
}

/**
 * Calculate hours from start and end time
 * @param {string} startTime - Start time in HH:MM format
 * @param {string} endTime - End time in HH:MM format
 * @param {string} date - Date in YYYY-MM-DD format
 * @returns {number} - Hours worked
 */
function calculateHours(startTime, endTime, date) {
    const startDateTime = new Date(`${date}T${startTime}`);
    let endDateTime = new Date(`${date}T${endTime}`);
    
    // Handle overnight shifts
    if (endDateTime < startDateTime) {
        endDateTime.setDate(endDateTime.getDate() + 1);
    }
    
    const diffMs = endDateTime - startDateTime;
    const hours = diffMs / (1000 * 60 * 60);
    
    return hours;
}

/**
 * Check if hours exceed 8 and show notification if they do
 * Only shows one notification at a time for new entries
 * @param {number} hours - Hours worked
 * @param {boolean} isNewEntry - Whether this is a new time entry
 * @returns {boolean} - Whether notification was shown
 */
function checkHoursAndNotify(hours, isNewEntry = false) {
    // Only show notification for new entries over 8 hours
    if (hours > 8.0 && isNewEntry) {
        showOverworkNotification(hours);
        return true;
    }
    return false;
}

/**
 * Attach notification listeners to time entry form
 */
function attachTimeEntryListeners() {
    const form = document.getElementById('add-time-entry-form');
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        const startTime = document.getElementById('startzeit').value;
        const endTime = document.getElementById('endzeit').value;
        const date = document.getElementById('datum').value;
        
        if (startTime && endTime && date) {
            const hours = calculateHours(startTime, endTime, date);
            checkHoursAndNotify(hours, true);
        }
    });
}

/**
 * Check existing time entries for overwork and highlight them visually
 */
function checkExistingEntries() {
    const timeEntries = document.querySelectorAll('#time-entries-tbody tr');
    timeEntries.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            const dateText = cells[3].textContent;
            const startTime = cells[4].textContent;
            const endTime = cells[5].textContent;
            
            if (dateText && startTime && endTime) {
                const hours = calculateHours(startTime, endTime, dateText);
                
                // Add visual indication for over 8 hours
                if (hours > 8.0) {
                    row.classList.add('overwork-warning');
                } else {
                    row.classList.remove('overwork-warning');
                }
            }
        }
    });
}

// Initialize and check existing entries on script load
initNotificationSystem();
checkExistingEntries();

// Observe changes to the time entries table and re-check for overwork
const observer = new MutationObserver(checkExistingEntries);
const timeEntriesTable = document.getElementById('time-entries-tbody');
if (timeEntriesTable) {
    observer.observe(timeEntriesTable, { childList: true, subtree: true });
}
