// Configuration de l'API
const API_BASE_URL = 'http://localhost:8002';

// État de l'application
let allProposals = [];
let filteredProposals = [];

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    loadDomains();
    loadProposals();
    setupEventListeners();
});

// Configuration des écouteurs d'événements
function setupEventListeners() {
    document.getElementById('filter-btn').addEventListener('click', applyFilters);
    document.getElementById('reset-btn').addEventListener('click', resetFilters);
}

// Charger les domaines disponibles
async function loadDomains() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/domains`);
        const data = await response.json();

        const domainSelect = document.getElementById('domain-filter');
        data.domains.forEach(domain => {
            const option = document.createElement('option');
            option.value = domain;
            option.textContent = formatDomain(domain);
            domainSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des domaines:', error);
    }
}

// Charger les propositions
async function loadProposals(domain = '', status = '') {
    try {
        showLoading();

        let url = `${API_BASE_URL}/api/v1/proposals`;
        const params = new URLSearchParams();
        if (domain) params.append('domain', domain);
        if (status) params.append('status', status);
        if (params.toString()) url += `?${params.toString()}`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        allProposals = await response.json();
        filteredProposals = allProposals;

        displayProposals(filteredProposals);
        updateStats(filteredProposals);
    } catch (error) {
        console.error('Erreur lors du chargement des propositions:', error);
        showError('Impossible de charger les propositions. Vérifiez que l\'API est démarrée.');
    }
}

// Afficher le chargement
function showLoading() {
    const container = document.getElementById('proposals-list');
    container.innerHTML = '<div class="loading">Chargement des propositions</div>';
}

// Afficher une erreur
function showError(message) {
    const container = document.getElementById('proposals-list');
    container.innerHTML = `
        <div class="error-message">
            <h3>Erreur</h3>
            <p>${message}</p>
        </div>
    `;
}

// Afficher les propositions
function displayProposals(proposals) {
    const container = document.getElementById('proposals-list');

    if (proposals.length === 0) {
        container.innerHTML = `
            <div class="loading">
                Aucune proposition trouvée avec ces critères.
            </div>
        `;
        return;
    }

    container.innerHTML = proposals.map(proposal => createProposalCard(proposal)).join('');

    // Ajouter les événements de clic
    document.querySelectorAll('.proposal-card').forEach(card => {
        card.addEventListener('click', () => {
            const proposalId = card.dataset.id;
            window.location.href = `proposal.html?id=${proposalId}`;
        });
    });
}

// Créer une carte de proposition
function createProposalCard(proposal) {
    const co2Text = proposal.co2_reduction_tonnes_10y
        ? `${formatNumber(proposal.co2_reduction_tonnes_10y)} t CO2`
        : 'N/A';

    const costText = proposal.total_cost_chf
        ? `${formatNumber(proposal.total_cost_chf)} CHF`
        : 'N/A';

    const votesText = proposal.total_votes > 0
        ? `${proposal.total_votes} vote${proposal.total_votes > 1 ? 's' : ''}`
        : 'Pas encore de vote';

    const avgScore = proposal.total_votes > 0
        ? ((proposal.avg_impact_score + proposal.avg_feasibility_score + proposal.avg_desirability_score) / 3).toFixed(1)
        : null;

    return `
        <div class="proposal-card" data-id="${proposal.id}">
            <span class="domain">${formatDomain(proposal.domain)}</span>
            <h3>${escapeHtml(proposal.title)}</h3>
            <p class="description">${escapeHtml(truncate(proposal.description, 150))}</p>
            <div class="meta">
                <span class="impact">${co2Text}</span>
                <span class="cost">${costText}</span>
            </div>
            <div class="meta">
                <span class="votes">${votesText}</span>
                ${avgScore ? `<span class="votes">Note: ${avgScore}/10</span>` : ''}
            </div>
            <span class="status">${formatStatus(proposal.status)}</span>
        </div>
    `;
}

// Mettre à jour les statistiques
function updateStats(proposals) {
    const totalProposals = proposals.length;
    const totalVotes = proposals.reduce((sum, p) => sum + p.total_votes, 0);
    const totalCO2 = proposals.reduce((sum, p) => sum + (p.co2_reduction_tonnes_10y || 0), 0);

    document.getElementById('total-proposals').textContent = totalProposals;
    document.getElementById('total-votes').textContent = totalVotes;
    document.getElementById('total-co2').textContent = formatNumber(totalCO2);
}

// Appliquer les filtres
function applyFilters() {
    const domain = document.getElementById('domain-filter').value;
    const status = document.getElementById('status-filter').value;
    loadProposals(domain, status);
}

// Réinitialiser les filtres
function resetFilters() {
    document.getElementById('domain-filter').value = '';
    document.getElementById('status-filter').value = '';
    loadProposals();
}

// Fonctions utilitaires

function formatDomain(domain) {
    const domains = {
        'transport': 'Transport',
        'energie': 'Énergie',
        'batiment': 'Bâtiment',
        'agriculture': 'Agriculture',
        'industrie': 'Industrie',
        'transversal': 'Transversal'
    };
    return domains[domain] || domain;
}

function formatStatus(status) {
    const statuses = {
        'generated': 'Générée',
        'validated': 'Validée',
        'simulation_complete': 'Simulation complète',
        'review': 'En révision',
        'voting': 'En vote',
        'approved': 'Approuvée'
    };
    return statuses[status] || status;
}

function formatNumber(num) {
    return new Intl.NumberFormat('fr-CH').format(Math.round(num));
}

function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
