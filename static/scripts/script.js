// Mobile menu toggle handler
function setupMobileMenu() {
    const menuButton = document.getElementById('menu-toggle') || document.getElementById('menu-button');
    if (menuButton) {
        menuButton.addEventListener('click', function() {
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        });
    }
}

// Common data structure for consistent category colors and data
const categoryData = {
    labels: ['Food & Dining', 'Entertainment', 'Transportation', 'Shopping', 'Utilities', 'Healthcare', 'Education'],
    colors: {
        background: [
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(201, 203, 207, 0.2)',
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)'
        ],
        border: [
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(201, 203, 207, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)'
        ]
    }
};

// Example data fetching functions
async function fetchPieChartData() {
    return {
        labels: categoryData.labels,
        data: [203.00, 47.74, 122.70, 128.75, 135.20, 140.00, 199.99]
    };
}

async function fetchLineChartData() {
    return {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        data: [500, 700, 800, 977.38]
    };
}

async function fetchBudgetData() {
    return {
        spent: 977.38,
        total: 2000.00,
        remaining: 1022.62,
        daily: 340.87
    };
}

async function fetchBarData() {
    return {
        labels: categoryData.labels,
        data: [203.00, 47.74, 122.70, 128.75, 135.20, 140.00, 199.99]
    };
}

// Chart rendering functions
async function renderPieChart() {
    const ctx = document.getElementById('categoryPieChart');
    if (!ctx) return;

    const chartData = await fetchPieChartData();

    new Chart(ctx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Spending by Category',
                data: chartData.data,
                backgroundColor: categoryData.colors.background,
                borderColor: categoryData.colors.border,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) label += ': ';
                            if (context.parsed !== null) {
                                label += new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD' 
                                }).format(context.parsed);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

async function renderBarChart() {
    const ctx = document.getElementById('categoryBarChart');
    if (!ctx) return;

    const chartData = await fetchBarData();

    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Spending by Category',
                data: chartData.data,
                backgroundColor: categoryData.colors.background,
                borderColor: categoryData.colors.border,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD' 
                            }).format(context.raw);
                        }
                    }
                }
            }
        }
    });
}

async function renderCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    const chartData = await fetchBarData();

    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Spending by Category',
                data: chartData.data,
                backgroundColor: categoryData.colors.background,
                borderColor: categoryData.colors.border,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const value = context.raw;
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD' 
                            }).format(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

async function renderLineChart() {
    const ctx = document.getElementById('spendingTrendChart');
    if (!ctx) return;

    const chartData = await fetchLineChartData();

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Spending Trend',
                data: chartData.data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

async function renderBudgetData() {
    const budgetData = await fetchBudgetData();
    const spentPercentage = (budgetData.spent / budgetData.total) * 100;

    // Update text displays
    document.getElementById('budget-spent')?.textContent = 
        `$${budgetData.spent.toFixed(2)} of $${budgetData.total.toFixed(2)}`;
    document.getElementById('budget-percentage')?.textContent = 
        `${Math.round(spentPercentage)}%`;
    
    // Animate progress bar
    const progressBar = document.getElementById('budget-bar');
    if (progressBar) {
        progressBar.style.width = `${spentPercentage}%`;
    }
}

// Expense form handling
function setupExpenseForm() {
    const form = document.querySelector('#expenses.html form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add actual form submission logic here
            alert('Expense added successfully!');
            form.reset();
        });
    }
}

// Budget question handling
function setupBudgetQuestion() {
    const questionForm = document.querySelector('.bg-white.rounded-lg.shadow div.flex');
    if (questionForm) {
        const button = questionForm.querySelector('button');
        const input = questionForm.querySelector('input');
        
        button.addEventListener('click', function() {
            if (input.value.trim()) {
                // Add actual AI question handling here
                alert(`Your question about "${input.value}" has been submitted to our AI!`);
                input.value = '';
            }
        });
    }
}

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupMobileMenu();
    setupExpenseForm();
    setupBudgetQuestion();
    
    // Render charts only if their containers exist
    if (document.getElementById('categoryPieChart')) renderPieChart();
    if (document.getElementById('spendingTrendChart')) renderLineChart();
    if (document.getElementById('categoryBarChart')) renderBarChart();
    if (document.getElementById('categoryChart')) renderCategoryChart();
    if (document.getElementById('budget-spent')) renderBudgetData();
});