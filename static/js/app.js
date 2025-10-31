// ============================================
// STATE MANAGEMENT
// ============================================
let currentProduct = null;
let userProfile = {
    age: 30,
    sex: 'homme'
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Application initialisée');

    // Charger le profil depuis localStorage
    loadUserProfile();

    // Afficher la date actuelle
    updateCurrentDate();

    // Charger le résumé du jour
    loadDailySummary();

    // Charger l'historique
    loadHistory(7);

    // Ajouter les listeners pour la touche Enter
    document.getElementById('barcode-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') searchBarcode();
    });

    document.getElementById('name-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') searchByName();
    });
});

// ============================================
// USER PROFILE MANAGEMENT
// ============================================
function loadUserProfile() {
    const saved = localStorage.getItem('userProfile');
    if (saved) {
        userProfile = JSON.parse(saved);
        document.getElementById('age').value = userProfile.age;
        document.getElementById('sex').value = userProfile.sex;
    }
    updateProfileDisplay();
}

function saveUserProfile() {
    localStorage.setItem('userProfile', JSON.stringify(userProfile));
}

function updateProfile() {
    const age = parseInt(document.getElementById('age').value);
    const sex = document.getElementById('sex').value;

    if (age < 18 || age > 120) {
        showToast('Veuillez entrer un âge valide (18-120 ans)', 'error');
        return;
    }

    userProfile = { age, sex };
    saveUserProfile();
    updateProfileDisplay();
    loadDailySummary();

    showToast('Profil mis à jour avec succès!', 'success');
}

function updateProfileDisplay() {
    const info = document.getElementById('profile-info');
    const ageGroup = getAgeGroup(userProfile.age);
    const sexLabel = userProfile.sex === 'homme' ? 'Homme' : 'Femme';

    info.innerHTML = `
        <strong>Profil actif:</strong> ${sexLabel}, ${userProfile.age} ans (${ageGroup})
    `;
}

function getAgeGroup(age) {
    if (age <= 40) return '18-40 ans';
    if (age <= 60) return '41-60 ans';
    return '61+ ans';
}

// ============================================
// TAB SWITCHING
// ============================================
function switchTab(tabName) {
    // Désactiver tous les tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Activer le tab sélectionné
    event.target.classList.add('active');
    document.getElementById(tabName + '-search').classList.add('active');

    // Effacer les résultats de recherche si on change de tab
    if (tabName === 'name') {
        document.getElementById('search-results').innerHTML = '';
    }
}

// ============================================
// PRODUCT SEARCH
// ============================================
async function searchBarcode() {
    const barcode = document.getElementById('barcode-input').value.trim();

    if (!barcode) {
        showToast('Veuillez entrer un code-barre', 'error');
        return;
    }

    showToast('Recherche en cours...', 'info');

    try {
        const response = await fetch(`/api/search/barcode/${barcode}`);
        const data = await response.json();

        if (data.success) {
            displayProductDetails(data.product);
            showToast('Produit trouvé!', 'success');
        } else {
            showToast(data.message, 'error');
            hideProductDetails();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors de la recherche', 'error');
        hideProductDetails();
    }
}

async function searchByName() {
    const query = document.getElementById('name-input').value.trim();

    if (!query) {
        showToast('Veuillez entrer un nom de produit', 'error');
        return;
    }

    showToast('Recherche en cours... Cela peut prendre jusqu\'à 30 secondes', 'info');

    try {
        const response = await fetch(`/api/search/name?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.products.length > 0) {
            displaySearchResults(data.products);
            showToast(`${data.count} produits trouvés`, 'success');
        } else {
            document.getElementById('search-results').innerHTML = `
                <div style="padding: 2rem; text-align: center; color: #64748b;">
                    <p style="margin-bottom: 1rem;">❌ Aucun produit trouvé</p>
                    <p style="font-size: 0.875rem;">
                        Essayez un terme plus simple ou utilisez le code-barre
                    </p>
                </div>
            `;
            showToast('Aucun produit trouvé', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors de la recherche', 'error');
    }
}

function displaySearchResults(products) {
    const container = document.getElementById('search-results');

    const html = products.map(product => `
        <div class="search-result-item" onclick="selectProduct('${product.code}')">
            <div class="result-name">${product.name}</div>
            <div class="result-brand">
                ${product.brands} ${product.nutriscore ? `• Nutri-Score: ${product.nutriscore}` : ''}
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

async function selectProduct(barcode) {
    document.getElementById('barcode-input').value = barcode;
    await searchBarcode();

    // Scroll vers les détails du produit
    document.getElementById('product-details').scrollIntoView({ behavior: 'smooth' });
}

// ============================================
// PRODUCT DISPLAY
// ============================================
function displayProductDetails(product) {
    currentProduct = product;

    const container = document.getElementById('product-info');

    container.innerHTML = `
        <div class="product-header">
            <h3 class="product-name">${product.name}</h3>
            <p class="product-brand">${product.brands || 'Marque non renseignée'}</p>
        </div>

        <div class="scores-grid">
            <div class="score-item">
                <span class="score-label">Nutri-Score</span>
                <span class="score-value">${product.nutriscore || 'N/A'}</span>
            </div>
            <div class="score-item">
                <span class="score-label">Groupe NOVA</span>
                <span class="score-value">${product.nova_group || 'N/A'}</span>
            </div>
            <div class="score-item">
                <span class="score-label">Eco-Score</span>
                <span class="score-value">${product.ecoscore || 'N/A'}</span>
            </div>
        </div>

        <div class="nutrition-grid">
            <div class="nutrition-item">
                <span class="nutrition-label">⚡ Énergie</span>
                <span class="nutrition-value">${formatValue(product.energy_kcal)} kcal</span>
            </div>
            <div class="nutrition-item">
                <span class="nutrition-label">💪 Protéines</span>
                <span class="nutrition-value">${formatValue(product.proteins)} g</span>
            </div>
            <div class="nutrition-item">
                <span class="nutrition-label">🍚 Glucides</span>
                <span class="nutrition-value">${formatValue(product.carbohydrates)} g</span>
            </div>
            <div class="nutrition-item">
                <span class="nutrition-label">🥑 Lipides</span>
                <span class="nutrition-value">${formatValue(product.fat)} g</span>
            </div>
            <div class="nutrition-item">
                <span class="nutrition-label">🌾 Fibres</span>
                <span class="nutrition-value">${formatValue(product.fiber)} g</span>
            </div>
            <div class="nutrition-item">
                <span class="nutrition-label">🧂 Sel</span>
                <span class="nutrition-value">${formatValue(product.salt)} g</span>
            </div>
        </div>

        ${product.allergens && product.allergens.length > 0 ? `
            <div style="margin-top: 1rem; padding: 1rem; background: #fef3c7; border-radius: 0.5rem;">
                <strong>⚠️ Allergènes:</strong><br>
                ${product.allergens.map(a => a.replace('en:', '')).join(', ')}
            </div>
        ` : ''}
    `;

    document.getElementById('product-details').style.display = 'block';
}

function hideProductDetails() {
    document.getElementById('product-details').style.display = 'none';
    currentProduct = null;
}

function formatValue(value) {
    return value !== null && value !== undefined ? value : 'N/A';
}

// ============================================
// ADD TO JOURNAL
// ============================================
async function addToJournal() {
    if (!currentProduct) {
        showToast('Aucun produit sélectionné', 'error');
        return;
    }

    const quantity = parseFloat(document.getElementById('quantity').value);

    if (!quantity || quantity <= 0) {
        showToast('Veuillez entrer une quantité valide', 'error');
        return;
    }

    try {
        const response = await fetch('/api/consumption/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                barcode: currentProduct.barcode,
                quantity: quantity
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`✅ ${currentProduct.name} ajouté au journal!`, 'success');

            // Recharger le résumé du jour
            setTimeout(() => {
                loadDailySummary();
                loadHistory(7);
            }, 500);

            // Réinitialiser la quantité
            document.getElementById('quantity').value = 100;
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors de l\'ajout au journal', 'error');
    }
}

// ============================================
// DAILY SUMMARY
// ============================================
async function loadDailySummary() {
    const loading = document.getElementById('loading');
    const content = document.getElementById('summary-content');

    loading.style.display = 'block';
    content.style.display = 'none';

    try {
        const response = await fetch(
            `/api/daily-summary?age=${userProfile.age}&sex=${userProfile.sex}`
        );
        const data = await response.json();

        if (data.success) {
            displayDailySummary(data);
            loading.style.display = 'none';
            content.style.display = 'block';
        } else {
            showToast('Erreur lors du chargement du résumé', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors du chargement du résumé', 'error');
        loading.style.display = 'none';
    }
}

function displayDailySummary(data) {
    const { summary, recommendations, percentages } = data;

    // Mise à jour des calories
    updateNutrientIndicator('calories', summary.total_kcal, recommendations.calories, percentages.calories);

    // Mise à jour des protéines
    updateNutrientIndicator('proteins', summary.total_proteins, recommendations.proteins, percentages.proteins);

    // Mise à jour des glucides
    updateNutrientIndicator('carbs', summary.total_carbs, recommendations.carbohydrates, percentages.carbohydrates);

    // Mise à jour des lipides
    updateNutrientIndicator('fat', summary.total_fat, recommendations.fat, percentages.fat);

    // Mise à jour du nombre de produits
    document.getElementById('products-count').textContent = summary.num_products;
}

function updateNutrientIndicator(nutrient, current, target, percentage) {
    // Arrondir les valeurs
    current = Math.round(current * 10) / 10;
    percentage = Math.round(percentage * 10) / 10;

    // Mettre à jour les valeurs
    document.getElementById(`${nutrient}-current`).textContent = current;
    document.getElementById(`${nutrient}-target`).textContent = target;
    document.getElementById(`${nutrient}-percentage`).textContent = `${percentage}%`;

    // Mettre à jour la barre de progression
    const progressBar = document.getElementById(`${nutrient}-progress`);
    const width = Math.min(percentage, 100);
    progressBar.style.width = `${width}%`;

    // Changer la couleur selon le pourcentage
    progressBar.classList.remove('medium', 'high');

    if (percentage >= 90) {
        progressBar.classList.add('high');
    } else if (percentage >= 70) {
        progressBar.classList.add('medium');
    }

    // Animation
    progressBar.style.transition = 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
}

// ============================================
// HISTORY
// ============================================
async function loadHistory(days = 7) {
    try {
        const response = await fetch(`/api/history?days=${days}`);
        const data = await response.json();

        if (data.success) {
            displayHistory(data.history);
        } else {
            showToast('Erreur lors du chargement de l\'historique', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur lors du chargement de l\'historique', 'error');
    }
}

function displayHistory(history) {
    const container = document.getElementById('history-content');

    if (!history || history.length === 0) {
        container.innerHTML = `
            <div style="padding: 2rem; text-align: center; color: #64748b;">
                <p>📭 Aucune consommation enregistrée</p>
            </div>
        `;
        return;
    }

    const html = history.slice(0, 20).map(entry => {
        const date = new Date(entry.timestamp);
        const dateStr = date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
        const timeStr = date.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const kcal = entry.energy_kcal
            ? Math.round((entry.energy_kcal * entry.quantity) / 100)
            : 0;

        return `
            <div class="history-item">
                <div class="history-date">🕐 ${dateStr} à ${timeStr}</div>
                <div class="history-product">${entry.product_name}</div>
                <div class="history-quantity">
                    Quantité: ${entry.quantity}${entry.unit}
                    ${kcal > 0 ? `• ${kcal} kcal` : ''}
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success' ? '✅' :
                 type === 'error' ? '❌' :
                 'ℹ️';

    toast.innerHTML = `
        <span style="font-size: 1.2rem;">${icon}</span>
        <span style="flex: 1;">${message}</span>
    `;

    container.appendChild(toast);

    // Supprimer après 4 secondes
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// UTILITIES
// ============================================
function updateCurrentDate() {
    const date = new Date();
    const dateStr = date.toLocaleDateString('fr-FR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const element = document.getElementById('current-date');
    if (element) {
        element.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    }
}

// Actualiser automatiquement toutes les 5 minutes
setInterval(() => {
    loadDailySummary();
}, 5 * 60 * 1000);

console.log('✅ JavaScript chargé avec succès');
