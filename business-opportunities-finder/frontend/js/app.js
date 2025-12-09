/**
 * Main application logic for Business Opportunities Finder
 */

// State
let currentFilters = {
    sector: '',
    status: '',
    min_score: '',
    search: ''
};

let searchTimeout = null;
let allOpportunities = [];

/**
 * Initialize app on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Business Opportunities Finder initialized');
    await loadDashboard();
});

/**
 * Load dashboard data
 */
async function loadDashboard() {
    try {
        // Load analytics for stats
        await loadAnalytics();

        // Load opportunities
        await loadOpportunities();

        // Populate sector filter
        await populateSectorFilter();

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

/**
 * Load analytics data
 */
async function loadAnalytics() {
    try {
        const analytics = await getAnalytics();

        // Update stats
        document.getElementById('totalOpportunities').textContent = analytics.total_opportunities;
        document.getElementById('avgScore').textContent = analytics.avg_score.toFixed(1);

        const statusCount = analytics.opportunities_by_status;
        document.getElementById('selectedCount').textContent = statusCount.selected || 0;

        if (analytics.top_sectors && analytics.top_sectors.length > 0) {
            document.getElementById('topSector').textContent = analytics.top_sectors[0].sector;
        } else {
            document.getElementById('topSector').textContent = 'N/A';
        }

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

/**
 * Load opportunities
 */
async function loadOpportunities() {
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const grid = document.getElementById('opportunitiesGrid');

    // Show loading
    loadingState.style.display = 'block';
    emptyState.style.display = 'none';
    grid.innerHTML = '';

    try {
        const data = await getOpportunities({
            ...currentFilters,
            limit: 50
        });

        allOpportunities = data.opportunities;

        // Hide loading
        loadingState.style.display = 'none';

        if (allOpportunities.length === 0) {
            emptyState.style.display = 'block';
        } else {
            renderOpportunities(allOpportunities);
        }

    } catch (error) {
        console.error('Error loading opportunities:', error);
        loadingState.style.display = 'none';
        showError('Failed to load opportunities');
    }
}

/**
 * Render opportunities to grid
 */
function renderOpportunities(opportunities) {
    const grid = document.getElementById('opportunitiesGrid');
    grid.innerHTML = '';

    opportunities.forEach(opp => {
        const card = createOpportunityCard(opp);
        grid.appendChild(card);
    });
}

/**
 * Create opportunity card element
 */
function createOpportunityCard(opp) {
    const card = document.createElement('div');
    card.className = 'opportunity-card';
    card.onclick = () => viewOpportunityDetail(opp.public_id);

    // Get proposed app details
    const proposedApp = opp.proposed_app || {};
    const features = proposedApp.key_features || [];
    const scoreBreakdown = opp.score_breakdown || {};

    // Status badge
    const statusColors = {
        'new': 'badge-status',
        'selected': 'badge-status',
        'in_progress': 'badge-status',
        'discarded': 'badge-sector'
    };

    const statusLabels = {
        'new': '🆕 New',
        'selected': '✅ Selected',
        'in_progress': '⚙️ In Progress',
        'discarded': '❌ Discarded'
    };

    card.innerHTML = `
        <div class="card-header">
            <div class="card-title">
                <h3>${escapeHtml(opp.title)}</h3>
                <div class="badges">
                    <span class="badge badge-sector">📂 ${escapeHtml(opp.sector || 'Unknown')}</span>
                    <span class="badge ${statusColors[opp.status] || 'badge-sector'}">
                        ${statusLabels[opp.status] || opp.status}
                    </span>
                </div>
            </div>
            <div class="score-pill">
                ${opp.score_total ? opp.score_total.toFixed(1) : 'N/A'}
            </div>
        </div>
        
        <div class="card-body">
            <p class="description">
                ${escapeHtml(truncateText(opp.problem_description, 200))}
            </p>
            
            ${features.length > 0 ? `
                <div class="features">
                    <h4>💡 Key Features</h4>
                    <ul>
                        ${features.slice(0, 3).map(f => `<li>${escapeHtml(f)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
        
        <div class="card-footer">
            <div class="meta-info">
                <span>💼 ${escapeHtml(proposedApp.name || 'N/A')}</span>
                <span>⏱️ ${escapeHtml(proposedApp.mvp_estimate || 'N/A')}</span>
                <span>💰 ${escapeHtml(proposedApp.pricing_model || 'N/A')}</span>
            </div>
        </div>
        
        ${Object.keys(scoreBreakdown).length > 0 ? `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--card-border);">
                <div class="score-breakdown">
                    ${scoreBreakdown.pain !== undefined ? `
                        <div class="score-item">
                            <span class="score-item-value">${scoreBreakdown.pain.toFixed(1)}</span>
                            <span class="score-item-label">Pain</span>
                        </div>
                    ` : ''}
                    ${scoreBreakdown.frequency !== undefined ? `
                        <div class="score-item">
                            <span class="score-item-value">${scoreBreakdown.frequency.toFixed(1)}</span>
                            <span class="score-item-label">Freq</span>
                        </div>
                    ` : ''}
                    ${scoreBreakdown.willingness_to_pay !== undefined ? `
                        <div class="score-item">
                            <span class="score-item-value">${scoreBreakdown.willingness_to_pay.toFixed(1)}</span>
                            <span class="score-item-label">Pay</span>
                        </div>
                    ` : ''}
                    ${scoreBreakdown.technical_feasibility !== undefined ? `
                        <div class="score-item">
                            <span class="score-item-value">${scoreBreakdown.technical_feasibility.toFixed(1)}</span>
                            <span class="score-item-label">Tech</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        ` : ''}
    `;

    return card;
}

/**
 * View opportunity detail (for MVP, just console log)
 */
function viewOpportunityDetail(opportunityId) {
    console.log('Viewing opportunity:', opportunityId);
    // In full implementation, would open a modal with full details
    alert(`Opportunity ID: ${opportunityId}\n\nFull detail modal coming soon!`);
}

/**
 * Populate sector filter dropdown
 */
async function populateSectorFilter() {
    try {
        const analytics = await getAnalytics();
        const select = document.getElementById('sectorFilter');

        // Clear existing options except "All"
        select.innerHTML = '<option value="">All Sectors</option>';

        // Add sectors from analytics
        if (analytics.top_sectors) {
            analytics.top_sectors.forEach(sector => {
                const option = document.createElement('option');
                option.value = sector.sector;
                option.textContent = `${sector.sector} (${sector.count})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error populating sector filter:', error);
    }
}

/**
 * Apply filters
 */
function applyFilters() {
    currentFilters = {
        sector: document.getElementById('sectorFilter').value,
        status: document.getElementById('statusFilter').value,
        min_score: document.getElementById('minScoreFilter').value,
        search: document.getElementById('searchInput').value
    };

    loadOpportunities();
}

/**
 * Debounced search
 */
function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        applyFilters();
    }, 500);
}

/**
 * Refresh opportunities
 */
async function refreshOpportunities() {
    await loadDashboard();
}

/**
 * Run manual discovery (calls the daily job)
 */
async function runManualDiscovery() {
    if (!confirm('Run manual discovery? This may take several minutes.')) {
        return;
    }

    alert('Manual discovery feature requires backend endpoint implementation.\nFor now, the scheduler runs automatically at 7:00 AM.');
}

/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Utility: Truncate text
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Utility: Show error
 */
function showError(message) {
    const grid = document.getElementById('opportunitiesGrid');
    grid.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <h2>Error</h2>
            <p style="color: var(--text-muted);">${escapeHtml(message)}</p>
        </div>
    `;
}
