/**
 * Navigation menu functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    setupMobileMenu();
});

async function initializeNavigation() {
    try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            console.log('No token found');
            return;
        }

        const response = await fetch('/api/user/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        updateNavigationBasedOnRole(userData);

    } catch (error) {
        console.error('Error initializing navigation:', error);
    }
}

function updateNavigationBasedOnRole(userData) {
    const adminLinkRoles = document.getElementById('adminLinkRoles');
    const adminLinkUsers = document.getElementById('adminLinkUsers');
    const adminLinkApprovals = document.getElementById('adminLinkApprovals');

    // Handle different role property structures
    let isAdmin = false;
    let isManager = false;

    if (userData.rolle_id === 1 || (userData.rolle && userData.rolle.name === 'Administrator')) {
        isAdmin = true;
    }
    if (userData.rolle_id === 2 || (userData.rolle && userData.rolle.name === 'Manager')) {
        isManager = true;
    }

    // Update visibility for admin/manager features
    if (adminLinkRoles) {
        adminLinkRoles.style.display = (isAdmin || isManager) ? 'inline-block' : 'none';
    }
    if (adminLinkUsers) {
        adminLinkUsers.style.display = isAdmin ? 'inline-block' : 'none';
    }
    if (adminLinkApprovals) {
        adminLinkApprovals.style.display = (isAdmin || isManager) ? 'inline-block' : 'none';
    }
}

function setupMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.querySelector('nav.main-nav ul');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('open');
            
            // Change icon based on menu state
            const icon = menuToggle.querySelector('i');
            if (icon) {
                icon.className = navMenu.classList.contains('open') ? 'fas fa-times' : 'fas fa-bars';
            }
        });
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('nav.main-nav') && !event.target.closest('#menu-toggle')) {
            if (navMenu && navMenu.classList.contains('open')) {
                navMenu.classList.remove('open');
                const icon = menuToggle?.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-bars';
                }
            }
        }
    });
}

// Logout function
function logout() {
    // Clear all storage
    localStorage.clear();
    sessionStorage.clear();
    
    // Clear cookies
    document.cookie.split(";").forEach(function(c) {
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
    
    // Redirect to Login page
    window.location.href = '/Login.html';
}
