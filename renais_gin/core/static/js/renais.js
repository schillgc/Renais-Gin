// Renais Gin Main JavaScript File

class RenaisApp {
    constructor() {
        this.apiBase = '/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateMovementMetrics();
        this.setupRealTimeUpdates();
        this.setupFormValidations();
        this.setupAnimations();
    }

    // Event Listeners
    setupEventListeners() {
        // Navigation mobile menu
        const navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler) {
            navbarToggler.addEventListener('click', this.toggleMobileMenu);
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', this.smoothScroll);
        });

        // Form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit);
        });

        // Modal triggers
        document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
            trigger.addEventListener('click', this.handleModalTrigger);
        });
    }

    // Movement Metrics
    async updateMovementMetrics() {
        try {
            const response = await fetch(`${this.apiBase}/metrics/`);
            const data = await response.json();

            this.updateMetricElements(data);
        } catch (error) {
            console.error('Error updating movement metrics:', error);
        }
    }

    updateMetricElements(data) {
        const metricSelectors = {
            'total-community': data.total_community,
            'total-pledges': data.total_pledges,
            'approved-pledges': data.approved_pledges,
            'total-impact': `$${data.total_impact}`,
            'total-bottles': data.total_bottles || 0,
            'environmental-count': data.environmental_impact || 0,
            'community-count': data.community_impact || 0,
            'education-count': data.education_impact || 0
        };

        for (const [selector, value] of Object.entries(metricSelectors)) {
            const elements = document.querySelectorAll(`[id="${selector}"]`);
            elements.forEach(element => {
                if (element.classList.contains('display-6') || element.classList.contains('display-4')) {
                    this.animateCounter(element, value);
                } else {
                    element.textContent = value;
                }
            });
        }
    }

    // Counter Animation
    animateCounter(element, targetValue) {
        const currentValue = parseInt(element.textContent.replace(/,/g, '')) || 0;
        const target = typeof targetValue === 'string'
            ? parseInt(targetValue.replace(/[^0-9]/g, ''))
            : targetValue;

        if (currentValue === target) return;

        const duration = 2000;
        const startTime = performance.now();
        const isCurrency = typeof targetValue === 'string' && targetValue.includes('$');

        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(currentValue + (target - currentValue) * easeOutQuart);

            element.textContent = isCurrency ? `$${current.toLocaleString()}` : current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = isCurrency ? `$${target.toLocaleString()}` : target.toLocaleString();
            }
        };

        requestAnimationFrame(updateCounter);
    }

    // Real-time Updates
    setupRealTimeUpdates() {
        // Update metrics every 30 seconds
        setInterval(() => this.updateMovementMetrics(), 30000);

        // WebSocket connection for live updates (placeholder)
        this.setupWebSocket();
    }

    setupWebSocket() {
        // This would connect to a WebSocket for real-time updates
        // For now, it's a placeholder for future implementation
        console.log('WebSocket setup would go here');
    }

    // Form Handling
    setupFormValidations() {
        // Pledge form validation
        const pledgeForm = document.querySelector('form[action*="pledge"]');
        if (pledgeForm) {
            pledgeForm.addEventListener('submit', this.validatePledgeForm);
        }

        // Bottle registration form validation
        const bottleForm = document.querySelector('form[action*="bottle"]');
        if (bottleForm) {
            bottleForm.addEventListener('submit', this.validateBottleForm);
        }
    }

    validatePledgeForm(event) {
        const form = event.target;
        const pledgeText = form.querySelector('#pledge_text');
        const impactPlan = form.querySelector('#impact_plan');
        let isValid = true;

        // Clear previous errors
        this.clearFormErrors(form);

        // Validate pledge text
        if (!pledgeText.value.trim()) {
            this.showFieldError(pledgeText, 'Pledge statement is required');
            isValid = false;
        } else if (pledgeText.value.trim().split(' ').length < 10) {
            this.showFieldError(pledgeText, 'Pledge should be more detailed (minimum 10 words)');
            isValid = false;
        }

        // Validate impact plan
        if (!impactPlan.value.trim()) {
            this.showFieldError(impactPlan, 'Impact plan is required');
            isValid = false;
        } else if (impactPlan.value.trim().split(' ').length < 15) {
            this.showFieldError(impactPlan, 'Please provide a more detailed plan (minimum 15 words)');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
            this.showToast('Please fix the errors in the form', 'error');
        }
    }

    validateBottleForm(event) {
        const form = event.target;
        const bottleId = form.querySelector('#id_bottle_id');
        let isValid = true;

        this.clearFormErrors(form);

        if (!bottleId.value.trim()) {
            this.showFieldError(bottleId, 'Bottle ID is required');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
            this.showToast('Please fix the errors in the form', 'error');
        }
    }

    clearFormErrors(form) {
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(feedback => {
            feedback.remove();
        });
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }

    // Toast Notifications
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.setAttribute('role', 'alert');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // Animations
    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe elements with animation classes
        document.querySelectorAll('.impact-card, .stat-card, .chart-container').forEach(el => {
            observer.observe(el);
        });
    }

    // Utility Methods
    smoothScroll(event) {
        event.preventDefault();
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    handleFormSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');

        if (submitBtn) {
            // Show loading state
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            submitBtn.disabled = true;

            // Re-enable button after form submission (handled by browser)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 3000);
        }
    }

    handleModalTrigger(event) {
        const modalId = this.getAttribute('data-bs-target');
        const modal = document.querySelector(modalId);

        if (modal) {
            // Add custom modal initialization here if needed
            console.log(`Opening modal: ${modalId}`);
        }
    }

    toggleMobileMenu() {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        navbarCollapse.classList.toggle('show');
    }

    // API Methods
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        const mergedOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(`${this.apiBase}${endpoint}`, mergedOptions);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showToast('An error occurred. Please try again.', 'error');
            throw error;
        }
    }

    // User-specific methods
    async getUserStats() {
        try {
            const data = await this.apiCall('/user/stats/');
            return data;
        } catch (error) {
            console.error('Failed to get user stats:', error);
            return null;
        }
    }

    async submitPledge(pledgeData) {
        try {
            const data = await this.apiCall('/pledges/', {
                method: 'POST',
                body: JSON.stringify(pledgeData)
            });

            this.showToast('Pledge submitted successfully!', 'success');
            return data;
        } catch (error) {
            console.error('Failed to submit pledge:', error);
            throw error;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.renaisApp = new RenaisApp();
});

// Utility functions
const RenaisUtils = {
    // Format numbers with commas
    formatNumber: (number) => {
        return new Intl.NumberFormat().format(number);
    },

    // Format currency
    formatCurrency: (amount, currency = 'USD') => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Format date
    formatDate: (dateString) => {
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },

    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Generate random ID
    generateId: (length = 8) => {
        return Math.random().toString(36).substr(2, length);
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RenaisApp, RenaisUtils };
}