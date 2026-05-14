// Shared Chart.js Defaults
Chart.defaults.color = '#8ba1b7';
Chart.defaults.font.family = 'Inter';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(10, 15, 26, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
Chart.defaults.plugins.tooltip.bodyColor = '#00d2ff';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;

// Initialize Dashboard Charts
function initDashboardCharts() {
    const weeklyCtx = document.getElementById('weeklyProgressChart');
    if (weeklyCtx) {
        new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Habits Completed',
                    data: [3, 4, 5, 2, 6, 4, 5],
                    borderColor: '#00d2ff',
                    backgroundColor: 'rgba(0, 210, 255, 0.1)',
                    borderWidth: 2,
                    pointBackgroundColor: '#0a0f1a',
                    pointBorderColor: '#00d2ff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        max: 8
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    const monthlyCtx = document.getElementById('monthlyConsistencyChart');
    if (monthlyCtx) {
        new Chart(monthlyCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Missed'],
                datasets: [{
                    data: [20, 10],
                    backgroundColor: ['#00e676', '#ff1744'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
}

// Initialize Analytics Charts
function initAnalyticsCharts() {
    const analyticsCtx = document.getElementById('analyticsChart');
    if (analyticsCtx) {
        new Chart(analyticsCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Completion',
                    data: [3, 4, 5, 2, 6, 4, 5],
                    borderColor: '#00d2ff',
                    backgroundColor: 'rgba(0, 210, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx) {
        new Chart(categoryCtx, {
            type: 'bar',
            data: {
                labels: ['Fitness', 'Reading', 'Meditation', 'Coding'],
                datasets: [{
                    label: 'Rate',
                    data: [80, 60, 90, 40],
                    backgroundColor: ['#00d2ff', '#3a7bd5', '#00e676', '#ff1744'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

// Handle Habit Toggling
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtns = document.querySelectorAll('.toggle-habit-btn');
    const completedCountSpan = document.getElementById('completedCount');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', async function() {
            const habitItem = this.closest('.habit-item');
            const habitId = habitItem.dataset.habitId;
            
            try {
                const response = await fetch(`/api/habits/${habitId}/toggle`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.completed) {
                        this.classList.remove('glass-btn');
                        this.classList.add('btn-success');
                        this.textContent = 'Completed';
                        if(completedCountSpan) {
                            completedCountSpan.textContent = parseInt(completedCountSpan.textContent) + 1;
                        }
                    } else {
                        this.classList.remove('btn-success');
                        this.classList.add('glass-btn');
                        this.textContent = 'Mark Complete';
                        if(completedCountSpan) {
                            completedCountSpan.textContent = parseInt(completedCountSpan.textContent) - 1;
                        }
                    }
                }
            } catch (error) {
                console.error('Error toggling habit:', error);
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.hide();
        }, 5000);
    });
});
