// Renais Gin Frontend Application

class RenaisApp {
    constructor() {
        this.apiBase = '/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Global event listeners can be added here
        console.log('Renais Gin App Initialized');
    }

    loadInitialData() {
        // Load initial data if user is authenticated
        if (this.isAuthenticated()) {
            this.loadUserStats();
        }
    }

    isAuthenticated() {
        // Check if user is authenticated (simplified check)
        return document.cookie.includes('sessionid');
    }

    async loadUserStats() {
        try {
            const response = await fetch(`${this.apiBase}/auth/stats/`);
            if (response.ok) {
                const stats = await response.json();
                this.updateDashboardStats(stats);
            }
        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    updateDashboardStats(stats) {
        // Update dashboard with user statistics
        const statsElements = {
            karmaScore: document.getElementById('karma-score'),
            totalPledges: document.getElementById('total-pledges'),
            approvedPledges: document.getElementById('approved-pledges'),
            totalRebates: document.getElementById('total-rebates')
        };

        for (const [key, element] of Object.entries(statsElements)) {
            if (element && stats[key]) {
                element.textContent = stats[key];
            }
        }
    }

    // Utility method for API calls
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(`${this.apiBase}${endpoint}`, finalOptions);
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Show notification
    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container') || document.querySelector('main');
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.renaisApp = new RenaisApp();
});

// Utility function for formatting numbers
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Utility function for formatting currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}