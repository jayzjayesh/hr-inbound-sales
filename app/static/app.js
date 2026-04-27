/**
 * Inbound Carrier Sales — Dashboard App
 * Fetches metrics from the API and renders Chart.js charts.
 */

const API_BASE = window.location.origin;
const REFRESH_INTERVAL = 30000; // 30 seconds

// Chart instances (for cleanup on refresh)
let charts = {};

// Color palette
const COLORS = {
    indigo: '#818cf8',
    purple: '#a78bfa',
    teal: '#2dd4bf',
    blue: '#60a5fa',
    green: '#34d399',
    amber: '#fbbf24',
    pink: '#f472b6',
    red: '#f87171',
    slate: '#94a3b8',
};

const OUTCOME_COLORS = {
    'Success': COLORS.green,
    'Rate too high': COLORS.amber,
    'Not interested': COLORS.slate,
    'Carrier not eligible': COLORS.red,
    'No loads available': COLORS.blue,
};

const SENTIMENT_COLORS = {
    'Positive': COLORS.green,
    'Neutral': COLORS.slate,
    'Negative': COLORS.red,
};

// ===== Chart.js Global Config =====
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 8;
Chart.defaults.plugins.legend.labels.padding = 16;

// ===== Fetch Metrics =====
async function fetchMetrics() {
    try {
        const res = await fetch(`${API_BASE}/api/v1/metrics`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('Failed to fetch metrics:', err);
        return null;
    }
}

// ===== Update KPI Cards =====
function updateKPIs(data) {
    animateValue('totalCalls', data.total_calls);
    document.getElementById('successRate').textContent = `${data.success_rate}%`;
    document.getElementById('avgRevenue').textContent = `$${data.avg_revenue.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    document.getElementById('avgSavings').textContent = `${data.avg_negotiation_savings}%`;
}

function animateValue(id, endValue) {
    const el = document.getElementById(id);
    const start = parseInt(el.textContent) || 0;
    const duration = 800;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = Math.round(start + (endValue - start) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ===== Render Charts =====
function renderOutcomesChart(data) {
    const ctx = document.getElementById('outcomesChart').getContext('2d');
    if (charts.outcomes) charts.outcomes.destroy();

    const labels = Object.keys(data.outcomes);
    const values = Object.values(data.outcomes);
    const colors = labels.map(l => OUTCOME_COLORS[l] || COLORS.slate);

    charts.outcomes = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'transparent',
                borderWidth: 0,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { font: { size: 11 }, padding: 12 },
                },
            },
        },
    });
}

function renderSentimentChart(data) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    if (charts.sentiment) charts.sentiment.destroy();

    const labels = Object.keys(data.sentiments);
    const values = Object.values(data.sentiments);
    const colors = labels.map(l => SENTIMENT_COLORS[l] || COLORS.slate);

    charts.sentiment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'transparent',
                borderWidth: 0,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { font: { size: 11 }, padding: 12 },
                },
            },
        },
    });
}

function renderVolumeChart(data) {
    const ctx = document.getElementById('volumeChart').getContext('2d');
    if (charts.volume) charts.volume.destroy();

    const labels = data.calls_over_time.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const values = data.calls_over_time.map(d => d.count);

    charts.volume = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Calls',
                data: values,
                backgroundColor: (ctx) => {
                    const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 260);
                    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.7)');
                    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.1)');
                    return gradient;
                },
                borderColor: COLORS.indigo,
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(51, 65, 85, 0.3)' },
                    ticks: { stepSize: 1, font: { size: 11 } },
                },
            },
        },
    });
}

function renderNegotiationChart(data) {
    const ctx = document.getElementById('negotiationChart').getContext('2d');
    if (charts.negotiation) charts.negotiation.destroy();

    const labels = data.negotiation_data.map(d => d.load_id || d.lane);
    const loadboardRates = data.negotiation_data.map(d => d.loadboard_rate);
    const agreedRates = data.negotiation_data.map(d => d.agreed_rate);

    charts.negotiation = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Loadboard Rate',
                    data: loadboardRates,
                    backgroundColor: 'rgba(99, 102, 241, 0.5)',
                    borderColor: COLORS.indigo,
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: 'Agreed Rate',
                    data: agreedRates,
                    backgroundColor: 'rgba(45, 212, 191, 0.5)',
                    borderColor: COLORS.teal,
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: { font: { size: 11 } },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(51, 65, 85, 0.3)' },
                    ticks: {
                        font: { size: 11 },
                        callback: (val) => `$${val.toLocaleString()}`,
                    },
                },
            },
        },
    });
}

function renderLanesChart(data) {
    const ctx = document.getElementById('lanesChart').getContext('2d');
    if (charts.lanes) charts.lanes.destroy();

    const labels = data.top_lanes.map(d => d.lane);
    const values = data.top_lanes.map(d => d.count);

    const barColors = [COLORS.indigo, COLORS.purple, COLORS.teal, COLORS.blue,
                       COLORS.green, COLORS.amber, COLORS.pink, COLORS.red];

    charts.lanes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: barColors.slice(0, values.length).map(c => c + '80'),
                borderColor: barColors.slice(0, values.length),
                borderWidth: 1,
                borderRadius: 4,
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: 'rgba(51, 65, 85, 0.3)' },
                    ticks: { stepSize: 1, font: { size: 11 } },
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } },
                },
            },
        },
    });
}

// ===== Render Table =====
function renderTable(data) {
    const tbody = document.getElementById('callsTableBody');
    tbody.innerHTML = '';

    data.recent_calls.forEach(call => {
        const tr = document.createElement('tr');

        const time = new Date(call.timestamp).toLocaleString('en-US', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
        });

        const lane = `${call.origin} → ${call.destination}`;

        const outcomeBadge = getOutcomeBadge(call.call_outcome);
        const sentimentBadge = getSentimentBadge(call.carrier_sentiment);

        const listedRate = call.loadboard_rate ? `$${call.loadboard_rate.toLocaleString()}` : '—';
        const agreedRate = call.agreed_rate ? `$${call.agreed_rate.toLocaleString()}` : '—';

        const duration = call.call_duration ? formatDuration(call.call_duration) : '—';

        tr.innerHTML = `
            <td>${time}</td>
            <td style="color: var(--text-primary); font-weight: 500;">${call.carrier_name}</td>
            <td>${lane}</td>
            <td>${call.equipment_type}</td>
            <td>${outcomeBadge}</td>
            <td>${sentimentBadge}</td>
            <td>${listedRate}</td>
            <td style="color: ${call.agreed_rate ? 'var(--accent-teal)' : 'inherit'}; font-weight: ${call.agreed_rate ? '600' : '400'};">${agreedRate}</td>
            <td>${call.negotiation_rounds || 0}</td>
            <td>${duration}</td>
        `;
        tbody.appendChild(tr);
    });
}

function getOutcomeBadge(outcome) {
    const classes = {
        'Success': 'badge-success',
        'Rate too high': 'badge-rate',
        'Not interested': 'badge-not-interested',
        'Carrier not eligible': 'badge-not-eligible',
        'No loads available': 'badge-no-loads',
    };
    const cls = classes[outcome] || 'badge-neutral';
    return `<span class="badge ${cls}">${outcome}</span>`;
}

function getSentimentBadge(sentiment) {
    const classes = {
        'Positive': 'badge-positive',
        'Neutral': 'badge-neutral',
        'Negative': 'badge-negative',
    };
    const cls = classes[sentiment] || 'badge-neutral';
    return `<span class="badge ${cls}">${sentiment}</span>`;
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, '0')}`;
}

// ===== Main =====
async function refreshDashboard() {
    const data = await fetchMetrics();
    if (!data) return;

    updateKPIs(data);
    renderOutcomesChart(data);
    renderSentimentChart(data);
    renderVolumeChart(data);
    renderNegotiationChart(data);
    renderLanesChart(data);
    renderTable(data);

    document.getElementById('lastUpdated').textContent =
        `Updated ${new Date().toLocaleTimeString()}`;
}

// Initial load
refreshDashboard();

// Auto-refresh
setInterval(refreshDashboard, REFRESH_INTERVAL);
