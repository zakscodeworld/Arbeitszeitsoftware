// Dashboard data loading and management
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/Login.html';
            return;
        }

        // Load user data
        const userData = await fetchUserData(token);
        updateWelcomeMessage(userData);

        // Load recent time entries
        const timeEntries = await fetchRecentTimeEntries(token);
        updateTimeEntriesTable(timeEntries);

        // Load upcoming absences
        const absences = await fetchUpcomingAbsences(token);
        updateAbsencesList(absences);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorNotification('Fehler beim Laden der Dashboard-Daten');
    }
}

async function fetchUserData(token) {
    const response = await fetch('/api/user/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch user data');
    }
    
    return await response.json();
}

function updateWelcomeMessage(userData) {
    const welcomeMessage = document.getElementById('welcomeMessage');
    const userName = userData.vorname && userData.nachname 
        ? `${userData.vorname} ${userData.nachname}`
        : 'Benutzer';
    welcomeMessage.textContent = `Willkommen, ${userName}!`;
}

async function fetchRecentTimeEntries(token) {
    const response = await fetch('/api/time_entries/recent', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch time entries');
    }
    
    return await response.json();
}

function updateTimeEntriesTable(entries) {
    const tableBody = document.getElementById('timeEntriesTableBody');
    
    if (!entries || entries.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5">Keine Einträge vorhanden</td></tr>';
        return;
    }

    tableBody.innerHTML = entries.map(entry => `
        <tr>
            <td>${formatDate(entry.datum)}</td>
            <td>${entry.projekt || '-'}</td>
            <td>${entry.aufgabe || '-'}</td>
            <td>${entry.dauer}</td>
            <td>${entry.kommentar || '-'}</td>
        </tr>
    `).join('');
}

async function fetchUpcomingAbsences(token) {
    const response = await fetch('/api/absences/upcoming', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch absences');
    }
    
    return await response.json();
}

function updateAbsencesList(absences) {
    const absencesList = document.getElementById('absencesList');
    
    if (!absences || absences.length === 0) {
        absencesList.innerHTML = '<li>Keine geplanten Abwesenheiten</li>';
        return;
    }

    absencesList.innerHTML = absences.map(absence => `
        <li>
            <span class="absence-date">${formatDateRange(absence.start_datum, absence.end_datum)}</span>
            <span class="absence-type">${absence.typ}</span>
            <span class="absence-status">${getStatusLabel(absence.status)}</span>
        </li>
    `).join('');
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('de-DE');
}

function formatDateRange(startDate, endDate) {
    return `${formatDate(startDate)} - ${formatDate(endDate)}`;
}

function getStatusLabel(status) {
    const statusLabels = {
        'pending': 'Ausstehend',
        'approved': 'Genehmigt',
        'rejected': 'Abgelehnt'
    };
    return statusLabels[status] || status;
}

function showErrorNotification(message) {
    // Use the existing notifications system
    if (typeof showNotification === 'function') {
        showNotification(message, 'error');
    } else {
        alert(message);
    }
}
