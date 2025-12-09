/**
 * API client for Business Opportunities Finder
 */

const API_BASE = window.location.origin + '/api';

/**
 * Generic API request function
 */
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Get opportunities with filters
 */
async function getOpportunities(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.sector) params.append('sector', filters.sector);
    if (filters.status) params.append('status', filters.status);
    if (filters.min_score) params.append('min_score', filters.min_score);
    if (filters.search) params.append('search', filters.search);
    if (filters.skip !== undefined) params.append('skip', filters.skip);
    if (filters.limit) params.append('limit', filters.limit);
    
    const queryString = params.toString();
    const endpoint = queryString ? `/opportunities?${queryString}` : '/opportunities';
    
    return await apiRequest(endpoint);
}

/**
 * Get single opportunity by ID
 */
async function getOpportunity(opportunityId) {
    return await apiRequest(`/opportunities/${opportunityId}`);
}

/**
 * Update opportunity (status, notes)
 */
async function updateOpportunity(opportunityId, data) {
    return await apiRequest(`/opportunities/${opportunityId}`, {
        method: 'PATCH',
        body: JSON.stringify(data)
    });
}

/**
 * Get analytics
 */
async function getAnalytics() {
    return await apiRequest('/analytics');
}

/**
 * Get latest report
 */
async function getLatestReport() {
    return await apiRequest('/reports/latest');
}

/**
 * Get report by date
 */
async function getReport(date) {
    return await apiRequest(`/reports/${date}`);
}

/**
 * Get sources
 */
async function getSources() {
    return await apiRequest('/sources');
}
