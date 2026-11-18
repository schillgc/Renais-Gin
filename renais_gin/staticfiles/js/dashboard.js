// Dashboard Specific JavaScript

class DashboardManager {
    constructor() {
        this.charts = new Map();
        this.init();
    }

    init() {
        this.initCharts();
        this.setupDashboardEvents();
        this.loadUserStats();
        this.setupRealTimeDashboard();
    }

    // Chart Initialization
    initCharts() {
        // Impact Distribution Chart
        this.initImpactDistributionChart();

        // Monthly Activity Chart
        this.initMonthlyActivityChart();

        // Progress Charts
        this.initProgressCharts();
    }

    initImpactDistributionChart() {
        const ctx = document.getElementById('impactDistributionChart');
        if (!ctx) return;

        // Mock data - in production, this would come from the API
        const data = {
            labels: ['Environmental', 'Community', 'Education', 'Other'],
            datasets: [{
                data: [45, 30, 20, 5],
                backgroundColor: [
                    '#10b981',
                    '#3b82f6',
                    '#f59e0b',
                    '#6b7280'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        this.charts.set('impactDistribution', new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        }));
    }

    initMonthlyActivityChart() {
        const ctx = document.getElementById('monthlyActivityChart');
        if (!ctx) return;

        const data = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            datasets: [{
                label: 'Pledges',
                data: [12, 19, 15, 25, 22, 30, 28],
                backgroundColor: 'rgba(212, 175, 55, 0.2)',
                borderColor: 'rgb(212, 175, 55)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }, {
                label: 'Approvals',
                data: [8, 12, 10, 18, 16, 22, 20],
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderColor: 'rgb(16, 185, 129)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        };

        this.charts.set('monthlyActivity', new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        }));
    }

    initProgressCharts() {
        // User progress chart
        const progressCtx = document.getElementById('userProgressChart');
        if (progressCtx) {
            this.charts.set('userProgress', new Chart(progressCtx, {
                type: 'bar',
                data: {
                    labels: ['Bottles', 'Pledges', 'Approvals', 'Impact'],
                    datasets: [{
                        data: [5, 3, 2, 10],
                        backgroundColor: [
                            'rgba(212, 175, 55, 0.8)',
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(139, 92, 246, 0.8)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }));
        }
    }

    // Event Handlers
    setupDashboardEvents() {
        // Refresh data button
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // Export data buttons
        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.exportData(e.target.dataset.type));
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleQuickAction(btn.dataset.action);
            });
        });
    }

    // Data Management
    async loadUserStats() {
        try {
            const stats = await window.renaisApp.getUserStats();
            if (stats) {
                this.updateUserStats(stats);
            }
        } catch (error) {
            console.error('Failed to load user stats:', error);
        }
    }

    updateUserStats(stats) {
        // Update various stat elements on the dashboard
        const statElements = {
            'user-bottles-count': stats.total_bottles,
            'user-pledges-count': stats.total_pledges,
            'user-approvals-count': stats.approved_pledges,
            'user-impact-amount': `$${stats.total_impact}`
        };

        for (const [elementId, value] of Object.entries(statElements)) {
            const element = document.getElementById(elementId);
            if (element) {
                if (element.classList.contains('stat-number')) {
                    window.renaisApp.animateCounter(element, value);
                } else {
                    element.textContent = value;
                }
            }
        }

        // Update progress bars
        this.updateProgressBars(stats);
    }

    updateProgressBars(stats) {
        const progressElements = {
            'bottles-progress': (stats.total_bottles / 10) * 100, // Assuming 10 is max for demonstration
            'pledges-progress': (stats.total_pledges / stats.total_bottles) * 100,
            'approval-progress': (stats.approved_pledges / stats.total_pledges) * 100
        };

        for (const [elementId, percentage] of Object.entries(progressElements)) {
            const element = document.getElementById(elementId);
            if (element) {
                element.style.width = `${Math.min(percentage, 100)}%`;
                element.setAttribute('aria-valuenow', percentage);
            }
        }
    }

    // Dashboard Actions
    refreshDashboard() {
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            const originalHtml = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Refreshing...';
            refreshBtn.disabled = true;

            Promise.all([
                window.renaisApp.updateMovementMetrics(),
                this.loadUserStats()
            ]).finally(() => {
                setTimeout(() => {
                    refreshBtn.innerHTML = originalHtml;
                    refreshBtn.disabled = false;
                    window.renaisApp.showToast('Dashboard updated successfully!', 'success');
                }, 1000);
            });
        }
    }

    handleQuickAction(action) {
        switch (action) {
            case 'register-bottle':
                window.location.href = '/bottles/register/';
                break;
            case 'submit-pledge':
                window.location.href = '/pledges/submit/';
                break;
            case 'view-stories':
                window.location.href = '/community/stories/';
                break;
            case 'join-circle':
                window.location.href = '/community/circles/';
                break;
            default:
                console.log('Unknown action:', action);
        }
    }

    exportData(type) {
        // This would generate and download data exports
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `renais-${type}-${timestamp}.csv`;

        // Mock export functionality
        window.renaisApp.showToast(`Exporting ${type} data...`, 'info');

        // Simulate download
        setTimeout(() => {
            window.renaisApp.showToast(`${type} data exported successfully!`, 'success');
        }, 2000);
    }

    // Real-time Dashboard Updates
    setupRealTimeDashboard() {
        // Update charts periodically
        setInterval(() => this.updateCharts(), 60000); // Every minute

        // Listen for custom events (e.g., from WebSocket)
        document.addEventListener('renais:data-update', (event) => {
            this.handleDataUpdate(event.detail);
        });
    }

    updateCharts() {
        // In a real application, this would fetch new data and update charts
        this.charts.forEach((chart, name) => {
            // Simulate data updates
            if (name === 'monthlyActivity') {
                const newData = chart.data.datasets[0].data.map(value =>
                    value + Math.floor(Math.random() * 5) - 2
                );
                chart.data.datasets[0].data = newData;
                chart.update('none');
            }
        });
    }

    handleDataUpdate(update) {
        // Handle real-time data updates from server
        console.log('Data update received:', update);

        if (update.type === 'metrics') {
            window.renaisApp.updateMovementMetrics();
        } else if (update.type === 'user_stats') {
            this.loadUserStats();
        }
    }

    // Utility Methods
    destroy() {
        // Clean up charts and event listeners
        this.charts.forEach(chart => {
            chart.destroy();
        });
        this.charts.clear();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on dashboard pages
    if (document.querySelector('[data-page="dashboard"]')) {
        window.dashboardManager = new DashboardManager();
    }
});