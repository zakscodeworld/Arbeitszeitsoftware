/**
 * API Error Handler for Invoice Integration
 * This module provides error handling for API calls
 */

/**
 * Process API response with advanced error handling
 * @param {Response} response - The fetch API response
 * @param {string} errorContext - Context description for error messages
 * @param {Function} successCallback - Function to call on success
 * @param {Function} errorCallback - Function to call on error
 * @returns {Promise} Promise resolving to the API data or error handling result
 */
async function handleApiResponse(response, errorContext, successCallback, errorCallback) {
    if (response.ok) {
        const data = await response.json();
        if (typeof successCallback === 'function') {
            return successCallback(data);
        }
        return data;
    }
    
    // Handle specific HTTP status codes
    switch (response.status) {
        case 401:
            // Unauthorized - handle token refresh or redirect to login
            console.error(`${errorContext}: Nicht autorisiert (401)`);
            
            // Try to refresh token
            const refreshSuccess = await refreshToken();
            if (refreshSuccess) {
                return { retry: true };
            } else {
                // Token refresh failed, redirect to login
                window.location.href = '/login.html';
                return null;
            }
        
        case 403:
            // Forbidden - user doesn't have permission
            console.error(`${errorContext}: Zugriff verweigert (403)`);
            displayMessage(`Zugriff verweigert. Sie haben keine Berechtigung für diese Aktion.`, 'error');
            break;
            
        case 404:
            // Not Found
            console.error(`${errorContext}: Ressource nicht gefunden (404)`);
            displayMessage(`Die angeforderte Ressource wurde nicht gefunden.`, 'warning');
            break;
            
        case 422:
            // Unprocessable Entity - validation error
            console.error(`${errorContext}: Validierungsfehler (422)`);
            
            // Try to get more detailed error information from response
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                        // Multiple validation errors
                        const errorMessages = errorData.detail.map(err => 
                            `${err.loc.join('.')}: ${err.msg}`
                        ).join('; ');
                        displayMessage(`Validierungsfehler: ${errorMessages}`, 'error');
                    } else {
                        // Single error message
                        displayMessage(`Validierungsfehler: ${errorData.detail}`, 'error');
                    }
                } else {
                    displayMessage(`Validierungsfehler bei der Anfrage.`, 'error');
                }
            } catch (e) {
                displayMessage(`Validierungsfehler bei der Anfrage.`, 'error');
            }
            break;
            
        case 500:
        case 502:
        case 503:
        case 504:
            // Server errors
            console.error(`${errorContext}: Serverfehler (${response.status})`);
            displayMessage(`Ein Serverfehler ist aufgetreten. Bitte versuchen Sie es später erneut.`, 'error');
            break;
            
        default:
            console.error(`${errorContext}: ${response.status} ${response.statusText}`);
            displayMessage(`Fehler: ${response.statusText}`, 'error');
    }
    
    if (typeof errorCallback === 'function') {
        return errorCallback(response);
    }
    
    return null;
}

/**
 * Enhanced fetch with automatic error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @param {string} errorContext - Context for error messages
 * @param {Function} successCallback - Function to call on success
 * @param {Function} errorCallback - Function to call on error 
 * @returns {Promise} Promise resolving to the API data
 */
async function fetchWithErrorHandling(url, options = {}, errorContext = 'API-Anfrage', successCallback, errorCallback) {
    try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            window.location.href = '/login.html';
            return null;
        }
        
        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        // Merge headers if options also has headers
        if (options.headers) {
            mergedOptions.headers = { ...defaultOptions.headers, ...options.headers };
        }
        
        const response = await fetch(url, mergedOptions);
        
        // Process response with error handling
        const result = await handleApiResponse(
            response, 
            errorContext,
            successCallback,
            errorCallback
        );
        
        // Handle retry if token was refreshed
        if (result && result.retry === true) {
            // Update token and retry request
            const newToken = localStorage.getItem('accessToken');
            if (newToken) {
                mergedOptions.headers['Authorization'] = `Bearer ${newToken}`;
                const retryResponse = await fetch(url, mergedOptions);
                return await handleApiResponse(
                    retryResponse,
                    errorContext,
                    successCallback,
                    errorCallback
                );
            }
        }
        
        return result;
    } catch (error) {
        console.error(`Netzwerkfehler (${errorContext}):`, error);
        displayMessage(`Verbindungsfehler: ${error.message}`, 'error');
        
        if (typeof errorCallback === 'function') {
            return errorCallback(error);
        }
        
        return null;
    }
}

/**
 * Error recovery - fallback data provider
 * @param {string} dataType - Type of data being requested
 * @returns {Object|Array} Fallback data
 */
function getFallbackData(dataType) {
    switch (dataType) {
        case 'user':
            return {
                id: 1,
                vorname: "Benutzer",
                nachname: "Lokal",
                email: "benutzer@bbqgmbh.de",
                role_id: 2
            };
            
        case 'timeEntries':
            return [];
            
        case 'projects':
            return [];
            
        case 'wageSettings':
            return {
                hourlyRates: {
                    'default': 125.00,
                    'Junior Developer': 85.00,
                    'Developer': 110.00, 
                    'Senior Developer': 140.00,
                    'Project Manager': 160.00
                },
                taxRates: {
                    'default': 0.19,
                    'reduced': 0.07
                }
            };
            
        default:
            return null;
    }
}

// Export the functions
window.ApiErrorHandler = {
    handleApiResponse,
    fetchWithErrorHandling,
    getFallbackData
};
