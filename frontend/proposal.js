// Configuration de l'API
const API_BASE_URL = 'http://localhost:8002';

// État
let currentProposal = null;
let proposalId = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    proposalId = getProposalIdFromUrl();
    if (!proposalId) {
        showError('ID de proposition manquant');
        return;
    }

    loadProposalDetail();
    setupVoteForm();
});

// Récupérer l'ID de la proposition depuis l'URL
function getProposalIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// Charger les détails de la proposition
async function loadProposalDetail() {
    try {
        showLoading();

        const response = await fetch(`${API_BASE_URL}/api/v1/proposals/${proposalId}`);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        currentProposal = await response.json();
        displayProposalDetail(currentProposal);

        // Afficher le formulaire de vote
        document.getElementById('vote-section').style.display = 'block';

        // Afficher le résumé des votes s'il y en a
        if (currentProposal.voting_summary && currentProposal.voting_summary.total_votes > 0) {
            displayVotingSummary(currentProposal.voting_summary);
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la proposition:', error);
        showError('Impossible de charger la proposition. Vérifiez que l\'API est démarrée.');
    }
}

// Afficher le chargement
function showLoading() {
    const container = document.getElementById('proposal-detail');
    container.innerHTML = '<div class="loading">Chargement de la proposition</div>';
}

// Afficher une erreur
function showError(message) {
    const container = document.getElementById('proposal-detail');
    container.innerHTML = `
        <div class="error-message">
            <h3>Erreur</h3>
            <p>${message}</p>
        </div>
    `;
}

// Afficher les détails de la proposition
function displayProposalDetail(proposal) {
    const container = document.getElementById('proposal-detail');

    let html = `
        <span class="domain-badge">${formatDomain(proposal.domain)}</span>
        <h2>${escapeHtml(proposal.title)}</h2>
        <p class="description">${escapeHtml(proposal.description)}</p>
    `;

    // Informations générales
    if (proposal.content) {
        const content = proposal.content;

        // Impact et budget
        html += '<div class="info-grid">';

        if (content.impact) {
            html += `
                <div class="info-item">
                    <strong>Réduction CO2 (10 ans)</strong>
                    <span>${formatNumber(content.impact.co2_reduction_tonnes_10y || 0)} tonnes</span>
                </div>
                <div class="info-item">
                    <strong>Réduction annuelle</strong>
                    <span>${formatNumber(content.impact.co2_reduction_tonnes_yearly || 0)} tonnes/an</span>
                </div>
            `;
        }

        if (content.budget) {
            html += `
                <div class="info-item">
                    <strong>Budget total</strong>
                    <span>${formatNumber(content.budget.total_chf)} CHF</span>
                </div>
            `;
        }

        if (content.implementation) {
            html += `
                <div class="info-item">
                    <strong>Durée</strong>
                    <span>${content.implementation.total_duration_years} an${content.implementation.total_duration_years > 1 ? 's' : ''}</span>
                </div>
            `;
        }

        html += '</div>';

        // Résumé
        if (content.summary) {
            html += `
                <div class="detail-section">
                    <h3>Résumé</h3>
                    <p>${escapeHtml(content.summary)}</p>
                </div>
            `;
        }

        // Actions
        if (content.actions && content.actions.length > 0) {
            html += `
                <div class="detail-section">
                    <h3>Actions principales</h3>
                    <ul>
                        ${content.actions.map(action => `<li>${escapeHtml(action)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Bénéfices additionnels
        if (content.impact && content.impact.additional_benefits) {
            html += `
                <div class="detail-section">
                    <h3>Bénéfices additionnels</h3>
                    <ul>
                        ${content.impact.additional_benefits.map(benefit => `<li>${escapeHtml(benefit)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Parties prenantes
        if (content.stakeholders && content.stakeholders.length > 0) {
            html += `
                <div class="detail-section">
                    <h3>Parties prenantes</h3>
                    <ul>
                        ${content.stakeholders.map(stakeholder => `<li>${escapeHtml(stakeholder)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Risques
        if (content.risks && content.risks.length > 0) {
            html += `
                <div class="detail-section">
                    <h3>Risques identifiés</h3>
                    <ul>
                        ${content.risks.map(risk => `
                            <li>
                                <strong>${escapeHtml(risk.description)}</strong>
                                (probabilité: ${risk.probability})
                                - Mitigation: ${escapeHtml(risk.mitigation)}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
    }

    // Validation
    if (proposal.validation) {
        const validation = proposal.validation;
        html += `
            <div class="detail-section">
                <h3>Validation</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Score de validation</strong>
                        <span>${validation.score}/10</span>
                    </div>
                    <div class="info-item">
                        <strong>Statut</strong>
                        <span>${validation.valid ? 'Valide' : 'Non valide'}</span>
                    </div>
                </div>
                ${validation.recommendations && validation.recommendations.length > 0 ? `
                    <p><strong>Recommandations:</strong></p>
                    <ul>
                        ${validation.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    }

    // Simulation
    if (proposal.simulation) {
        const simulation = proposal.simulation;
        html += `
            <div class="detail-section">
                <h3>Simulation d'impact</h3>
        `;

        if (simulation.co2_impact) {
            html += `
                <p><strong>Impact CO2 sur différentes périodes:</strong></p>
                <div class="info-grid">
                    ${simulation.co2_impact.totals ? `
                        <div class="info-item">
                            <strong>5 ans</strong>
                            <span>${formatNumber(simulation.co2_impact.totals['5_years'])} tonnes</span>
                        </div>
                        <div class="info-item">
                            <strong>10 ans</strong>
                            <span>${formatNumber(simulation.co2_impact.totals['10_years'])} tonnes</span>
                        </div>
                        <div class="info-item">
                            <strong>20 ans</strong>
                            <span>${formatNumber(simulation.co2_impact.totals['20_years'])} tonnes</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        if (simulation.economic_impact && simulation.economic_impact.roi) {
            html += `
                <p><strong>Analyse économique:</strong></p>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Coût par tonne CO2</strong>
                        <span>${formatNumber(simulation.economic_impact.roi.cost_per_tonne_co2)} CHF</span>
                    </div>
                    <div class="info-item">
                        <strong>ROI (10 ans)</strong>
                        <span>${simulation.economic_impact.roi.roi_10y_percent.toFixed(1)}%</span>
                    </div>
                </div>
            `;
        }

        if (simulation.feasibility) {
            html += `
                <p><strong>Faisabilité:</strong> ${simulation.feasibility.score}/10</p>
            `;
        }

        html += '</div>';
    }

    container.innerHTML = html;
}

// Afficher le résumé des votes
function displayVotingSummary(summary) {
    document.getElementById('votes-summary').style.display = 'block';
    document.getElementById('total-votes-count').textContent = summary.total_votes;
    document.getElementById('avg-impact').textContent = summary.avg_impact_score.toFixed(1);
    document.getElementById('avg-feasibility').textContent = summary.avg_feasibility_score.toFixed(1);
    document.getElementById('avg-desirability').textContent = summary.avg_desirability_score.toFixed(1);
    document.getElementById('avg-overall').textContent = summary.avg_overall_score.toFixed(1);
}

// Configuration du formulaire de vote
function setupVoteForm() {
    // Mise à jour des valeurs des sliders
    const impactScore = document.getElementById('impact-score');
    const feasibilityScore = document.getElementById('feasibility-score');
    const desirabilityScore = document.getElementById('desirability-score');

    const impactValue = document.getElementById('impact-value');
    const feasibilityValue = document.getElementById('feasibility-value');
    const desirabilityValue = document.getElementById('desirability-value');

    impactScore.addEventListener('input', (e) => {
        impactValue.textContent = e.target.value;
    });

    feasibilityScore.addEventListener('input', (e) => {
        feasibilityValue.textContent = e.target.value;
    });

    desirabilityScore.addEventListener('input', (e) => {
        desirabilityValue.textContent = e.target.value;
    });

    // Soumission du formulaire
    document.getElementById('vote-form').addEventListener('submit', handleVoteSubmit);
}

// Gérer la soumission du vote
async function handleVoteSubmit(e) {
    e.preventDefault();

    const voteData = {
        impact_score: parseInt(document.getElementById('impact-score').value),
        feasibility_score: parseInt(document.getElementById('feasibility-score').value),
        desirability_score: parseInt(document.getElementById('desirability-score').value),
        comment: document.getElementById('comment').value || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/proposals/${proposalId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(voteData)
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const result = await response.json();

        // Afficher le message de succès
        document.getElementById('vote-form').style.display = 'none';
        document.getElementById('vote-success').style.display = 'block';
        document.getElementById('vote-error').style.display = 'none';

        // Recharger les statistiques de vote
        setTimeout(() => {
            loadVotingSummary();
        }, 1000);

    } catch (error) {
        console.error('Erreur lors de l\'envoi du vote:', error);
        document.getElementById('vote-error').style.display = 'block';
        document.getElementById('error-text').textContent =
            'Une erreur est survenue lors de l\'envoi de votre vote. Veuillez réessayer.';
    }
}

// Charger le résumé des votes
async function loadVotingSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/proposals/${proposalId}/votes`);
        if (response.ok) {
            const summary = await response.json();
            if (summary.total_votes > 0) {
                displayVotingSummary(summary);
            }
        }
    } catch (error) {
        console.error('Erreur lors du chargement du résumé des votes:', error);
    }
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

function formatNumber(num) {
    return new Intl.NumberFormat('fr-CH').format(Math.round(num));
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
