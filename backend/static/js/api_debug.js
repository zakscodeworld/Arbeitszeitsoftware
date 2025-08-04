// Debugging-Hilfsfunktionen für die BBQ GmbH Zeiterfassung
// Diese Datei enthält Funktionen zur verbesserten Fehlerdiagnose der API-Kommunikation

// Globale Variable für Debug-Modus
let API_DEBUG = true;

/**
 * Verbesserte Fehlerprotokollierung mit API-Debug-Informationen
 * @param {string} message - Die Nachricht zum Protokollieren
 * @param {*} data - Optionale Daten zum Protokollieren
 */
function logDebug(message, data = null) {
    if (!API_DEBUG) return;
    
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] 🔍 ${message}`);
    
    if (data) {
        console.log('📦 Daten:', data);
    }
}

/**
 * Hilfsfunktion zum Anzeigen von Fehlermeldungen auf der Seite
 * @param {string} message - Die anzuzeigende Fehlermeldung
 * @param {string} type - Der Typ der Nachricht ('error', 'success', 'warning', 'info')
 * @param {number} duration - Anzeigedauer in Millisekunden (0 für dauerhaft)
 */
function showMessage(message, type = 'error', duration = 5000) {
    // Suche nach einem vorhandenen Message-Container oder erstelle einen neuen
    let messageArea = document.getElementById('message-area');
    
    if (!messageArea) {
        messageArea = document.createElement('div');
        messageArea.id = 'message-area';
        messageArea.style.position = 'fixed';
        messageArea.style.top = '70px';
        messageArea.style.left = '50%';
        messageArea.style.transform = 'translateX(-50%)';
        messageArea.style.zIndex = '1000';
        messageArea.style.width = '80%';
        messageArea.style.maxWidth = '500px';
        document.body.appendChild(messageArea);
    }
    
    // Erstelle die Nachrichtenbox
    const msgBox = document.createElement('div');
    msgBox.className = `message ${type}`;
    msgBox.style.padding = '10px 15px';
    msgBox.style.marginBottom = '10px';
    msgBox.style.borderRadius = '4px';
    msgBox.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    
    // Setze Farben basierend auf dem Nachrichtentyp
    switch(type) {
        case 'error':
            msgBox.style.backgroundColor = '#ffebee';
            msgBox.style.borderLeft = '4px solid #f44336';
            break;
        case 'success':
            msgBox.style.backgroundColor = '#e8f5e9';
            msgBox.style.borderLeft = '4px solid #4caf50';
            break;
        case 'warning':
            msgBox.style.backgroundColor = '#fff8e1';
            msgBox.style.borderLeft = '4px solid #ff9800';
            break;
        case 'info':
            msgBox.style.backgroundColor = '#e3f2fd';
            msgBox.style.borderLeft = '4px solid #2196f3';
            break;
    }
    
    // Erstelle den Nachrichtentext
    const msgText = document.createElement('p');
    msgText.style.margin = '0';
    msgText.textContent = message;
    
    // Füge den Text zur Box hinzu
    msgBox.appendChild(msgText);
    
    // Füge die Box zum Container hinzu
    messageArea.appendChild(msgBox);
    
    // Entferne die Nachricht nach der angegebenen Dauer (wenn nicht 0)
    if (duration > 0) {
        setTimeout(() => {
            if (msgBox && msgBox.parentNode) {
                msgBox.parentNode.removeChild(msgBox);
            }
        }, duration);
    }
    
    return msgBox;
}

/**
 * Verbesserte Funktion zum Abrufen von Daten mit Authentifizierung und Fehlerbehandlung
 * @param {string} url - Die URL zum Abrufen der Daten
 * @param {Object} options - Fetch-Optionen
 * @returns {Promise} - Promise mit der Antwort
 */
async function fetchWithAuthAndDebug(url, options = {}) {
    logDebug(`API-Anfrage an: ${url}`, options);
    
    try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            logDebug('Kein Zugriffstoken gefunden - Weiterleitung zur Anmeldeseite');
            window.location.href = '/login.html';
            return null;
        }
        
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        logDebug('Sende Anfrage mit Headern:', headers);
        
        const startTime = performance.now();
        const response = await fetch(url, { ...options, headers });
        const endTime = performance.now();
        
        logDebug(`Antwort erhalten (${Math.round(endTime - startTime)}ms):`, {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries([...response.headers])
        });
        
        if (response.status === 401 || response.status === 403) {
            logDebug(`Authentifizierungsfehler: ${response.status}`);
            localStorage.removeItem('accessToken');
            showMessage('Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.', 'warning');
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 2000);
            return null;
        }
        
        // Prüfen, ob die Antwort erfolgreich war, aber nicht für DELETE-Anfragen, die möglicherweise 204 zurückgeben
        if (!response.ok && options.method !== 'DELETE') {
            try {
                // Versuche, Fehlerdetails zu erhalten
                const errorBody = await response.text();
                let errorJson = {};
                
                try {
                    errorJson = JSON.parse(errorBody);
                } catch (e) {
                    // Falls keine gültige JSON-Antwort, verwende den Rohtext
                }
                
                logDebug(`API-Fehler: ${response.status} ${response.statusText}`, {
                    errorBody: errorBody.length > 500 ? errorBody.substring(0, 500) + '...' : errorBody,
                    errorJson
                });
            } catch (e) {
                logDebug(`Fehler beim Analysieren der Fehlerantwort: ${e.message}`);
            }
        }
        
        return response;
    } catch (error) {
        logDebug(`Netzwerkfehler bei Anfrage an ${url}:`, error);
        showMessage(`Netzwerkfehler: ${error.message}. Bitte überprüfen Sie Ihre Internetverbindung.`, 'error');
        throw error;
    }
}

/**
 * Hilfsfunktion zum Abrufen und Validieren von JSON-Daten von einer API
 * @param {string} url - API-URL
 * @param {Object} options - Fetch-Optionen
 * @param {function} validator - Optionale Validierungsfunktion für die Daten
 * @returns {Promise<Object>} - Verarbeitete Daten oder null bei Fehler
 */
async function fetchJsonWithValidation(url, options = {}, validator = null) {
    try {
        const response = await fetchWithAuthAndDebug(url, options);
        
        if (!response || !response.ok) {
            // Fehler bereits in fetchWithAuthAndDebug protokolliert
            return null;
        }
        
        let data;
        try {
            data = await response.json();
        } catch (error) {
            logDebug(`Fehler beim Parsen der JSON-Antwort von ${url}:`, error);
            showMessage('Fehler: Die vom Server empfangenen Daten sind ungültig.', 'error');
            return null;
        }
        
        // Datenvalidierung, falls angegeben
        if (validator && typeof validator === 'function') {
            const validationResult = validator(data);
            if (validationResult !== true) {
                logDebug(`Validierungsfehler für Daten von ${url}:`, validationResult);
                showMessage(`Fehler: ${validationResult}`, 'error');
                return null;
            }
        }
        
        return data;
    } catch (error) {
        logDebug(`Unbehandelte Ausnahme bei fetchJsonWithValidation für ${url}:`, error);
        showMessage(`Unerwarteter Fehler: ${error.message}`, 'error');
        return null;
    }
}

/**
 * Testet die Verbindung zu einem API-Endpunkt und gibt Diagnoseinformationen zurück
 * @param {string} endpoint - Der zu testende API-Endpunkt (z.B. '/users/')
 * @param {string} baseUrl - Die Basis-URL der API, standardmäßig '/api/v1'
 * @returns {Promise<Object>} - Diagnoseergebnis
 */
async function testApiEndpoint(endpoint, baseUrl = '/api/v1') {
    const url = `${baseUrl}${endpoint}`;
    logDebug(`Teste API-Endpunkt: ${url}`);
    
    const result = {
        endpoint,
        url,
        success: false,
        status: null,
        statusText: null,
        responseTime: null,
        errorDetails: null,
        responseData: null
    };
    
    try {
        const startTime = performance.now();
        const response = await fetchWithAuthAndDebug(url);
        const endTime = performance.now();
        
        result.responseTime = Math.round(endTime - startTime);
        result.status = response ? response.status : null;
        result.statusText = response ? response.statusText : 'Keine Antwort';
        
        if (response && response.ok) {
            result.success = true;
            
            // Versuche, die Antwortdaten zu lesen (aber limitiere die Größe für das Logging)
            try {
                const responseText = await response.text();
                result.responseSize = responseText.length;
                
                // Versuche, die Antwort als JSON zu parsen
                try {
                    result.responseData = JSON.parse(responseText);
                    
                    // Für Benutzer-Endpunkte zähle die Anzahl der Benutzer
                    if (endpoint.includes('/users')) {
                        if (Array.isArray(result.responseData)) {
                            result.userCount = result.responseData.length;
                        }
                    }
                } catch (e) {
                    result.responseData = {
                        text: responseText.length > 200 ? 
                            responseText.substring(0, 200) + '...' : 
                            responseText,
                        parseError: e.message
                    };
                }
            } catch (e) {
                result.errorDetails = `Fehler beim Lesen der Antwort: ${e.message}`;
            }
        } else {
            result.success = false;
            result.errorDetails = response ? 
                `HTTP-Fehler: ${response.status} ${response.statusText}` : 
                'Keine Antwort vom Server';
        }
    } catch (error) {
        result.success = false;
        result.errorDetails = `Ausnahme: ${error.message}`;
        logDebug(`Fehler beim Testen des Endpunkts ${url}:`, error);
    }
    
    logDebug(`API-Test für ${url} abgeschlossen:`, result);
    return result;
}

/**
 * Testet mehrere wichtige API-Endpunkte und zeigt Diagnoseergebnisse an
 * @param {Array<string>} endpoints - Liste der zu testenden Endpunkte
 * @param {function} callback - Callback-Funktion, die mit den Ergebnissen aufgerufen wird
 */
async function runApiDiagnostics(endpoints = ['/users/', '/roles/'], callback = null) {
    const results = [];
    
    for (const endpoint of endpoints) {
        const result = await testApiEndpoint(endpoint);
        results.push(result);
    }
    
    if (typeof callback === 'function') {
        callback(results);
    }
    
    return results;
}
