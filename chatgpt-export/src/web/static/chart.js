Chart.defaults.color = '#e0e0e0';
Chart.defaults.borderColor = 'rgba(255,255,255,0.08)';

const COLORS = [
    '#e94560', '#0f3460', '#10b981', '#f59e0b', '#8b5cf6',
    '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16',
];

function createLineChart(canvasId, labels, datasets, options) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#ccc', boxWidth: 12, padding: 12 },
                },
            },
            scales: {
                x: {
                    ticks: { color: '#888', maxTicksLimit: 12 },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#888' },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
            },
            ...options,
        },
    });
}

function createPieChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: COLORS.slice(0, labels.length),
                borderColor: '#1a1a2e',
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#ccc', boxWidth: 12, padding: 10, font: { size: 11 } },
                },
            },
        },
    });
}

function createBarChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#ccc', boxWidth: 12, padding: 12 },
                },
            },
            scales: {
                x: {
                    ticks: { color: '#888', maxTicksLimit: 15 },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#888' },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
            },
        },
    });
}

function createDoughnutChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: COLORS.slice(0, labels.length),
                borderColor: '#1a1a2e',
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#ccc', boxWidth: 12, padding: 10, font: { size: 11 } },
                },
            },
        },
    });
}

function createAreaChart(canvasId, labels, datasets) {
    const filled = datasets.map(d => ({
        ...d,
        fill: true,
        tension: 0.3,
    }));
    return createLineChart(canvasId, labels, filled, {
        ...Chart.defaults,
    });
}
