# 🍎 NutriTracker - Analyseur Nutritionnel Web

Application web dynamique et professionnelle pour l'analyse nutritionnelle avec indicateurs de contribution aux apports journaliers recommandés (AJR).

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-3.0+-red)

## ✨ Fonctionnalités

### 📊 **Suivi des Apports Journaliers Recommandés**
- Calcul personnalisé des AJR selon l'**âge** et le **sexe**
- Indicateurs visuels de progression dynamiques
- Barres de progression colorées selon le niveau d'atteinte:
  - 🟢 **Vert** : < 70% (sous les objectifs)
  - 🟠 **Orange** : 70-90% (proche des objectifs)
  - 🔴 **Rouge** : > 90% (objectifs atteints ou dépassés)

### 🔍 **Recherche de Produits**
- **Recherche par code-barre** : Scan ou saisie manuelle
- **Recherche par nom** : Base de 2,9M+ produits (OpenFoodFacts)
- Affichage détaillé des informations nutritionnelles
- Nutri-Score, NOVA, Eco-Score

### 📈 **Suivi Nutritionnel**
- **Calories** : Énergie totale consommée
- **Protéines** : Macronutriments essentiels
- **Glucides** : Source d'énergie principale
- **Lipides** : Graisses et acides gras

### 📜 **Historique des Consommations**
- Journal complet de vos consommations
- Filtrage par période (7, 30 jours)
- Détails par produit avec quantités et calories

### 👤 **Profil Utilisateur Personnalisé**
- Âge et sexe
- Calcul automatique des AJR selon:
  - **3 tranches d'âge** : 18-40 ans, 41-60 ans, 61+ ans
  - **2 sexes** : Homme, Femme
  - Recommandations basées sur l'ANSES (France) et EFSA (Europe)

## 📋 Prérequis

- Python 3.8 ou supérieur
- Connexion Internet (pour accéder à l'API OpenFoodFacts)

## 🚀 Installation

### 1. Cloner le dépôt
```bash
git clone <url-du-repo>
cd Nutrition_Analysis
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

ou manuellement:
```bash
pip install flask requests
```

## 🎯 Utilisation

### Lancer l'application web

```bash
python web_app.py
```

L'application sera accessible sur:
- **Local**: http://127.0.0.1:5000
- **Réseau**: http://votre-ip:5000

### Interface web

1. **Configurer votre profil**
   - Entrez votre âge (18-120 ans)
   - Sélectionnez votre sexe
   - Cliquez sur "Mettre à jour"

2. **Rechercher un produit**
   - **Option 1**: Entrez un code-barre (ex: 3017624010701)
   - **Option 2**: Recherchez par nom (ex: Nutella, Coca Cola)

3. **Ajouter au journal**
   - Sélectionnez un produit
   - Entrez la quantité consommée (en grammes)
   - Cliquez sur "Ajouter"

4. **Suivre vos apports**
   - Les indicateurs se mettent à jour automatiquement
   - Visualisez votre progression vers les objectifs quotidiens
   - Consultez l'historique de vos consommations

## 📊 Apports Journaliers Recommandés

### Homme

| Âge | Calories | Protéines | Glucides | Lipides | Fibres | Sel (max) |
|-----|----------|-----------|----------|---------|--------|-----------|
| 18-40 | 2500 kcal | 70g | 310g | 90g | 30g | 6g |
| 41-60 | 2350 kcal | 65g | 290g | 85g | 30g | 6g |
| 61+ | 2150 kcal | 70g | 265g | 75g | 30g | 5g |

### Femme

| Âge | Calories | Protéines | Glucides | Lipides | Fibres | Sel (max) |
|-----|----------|-----------|----------|---------|--------|-----------|
| 18-40 | 2000 kcal | 55g | 250g | 70g | 25g | 6g |
| 41-60 | 1900 kcal | 55g | 235g | 65g | 25g | 6g |
| 61+ | 1800 kcal | 60g | 220g | 60g | 25g | 5g |

*Source: ANSES (Agence nationale de sécurité sanitaire) et EFSA (European Food Safety Authority)*

## 🏗️ Architecture

```
Nutrition_Analysis/
│
├── web_app.py              # Application Flask principale
├── nutrition_app_python_final.py  # Logique métier
│
├── templates/
│   └── index.html          # Interface HTML
│
├── static/
│   ├── css/
│   │   └── style.css       # Styles CSS modernes
│   └── js/
│       └── app.js          # Logique JavaScript
│
├── requirements.txt        # Dépendances Python
├── nutrition_data.db       # Base de données SQLite (auto-créée)
└── README_WEB_APP.md      # Documentation
```

## 🎨 Design & UI/UX

### Technologies utilisées
- **HTML5** : Structure sémantique
- **CSS3** : Design moderne avec variables CSS
- **JavaScript** (Vanilla) : Interactions dynamiques
- **Flask** : Backend Python léger
- **SQLite** : Stockage local des données

### Caractéristiques du design
- ✅ Design responsive (mobile, tablette, desktop)
- ✅ Interface intuitive et claire
- ✅ Animations fluides et transitions
- ✅ Code couleur intuitif pour les indicateurs
- ✅ Toast notifications pour les retours utilisateur
- ✅ Thème moderne avec dégradés

## 🔧 API Endpoints

### GET `/api/recommendations`
Récupère les recommandations nutritionnelles pour un profil

**Paramètres:**
- `age` (int): Âge de l'utilisateur
- `sex` (string): 'homme' ou 'femme'

**Exemple:**
```bash
curl "http://localhost:5000/api/recommendations?age=30&sex=homme"
```

### GET `/api/search/barcode/<barcode>`
Recherche un produit par code-barre

**Exemple:**
```bash
curl "http://localhost:5000/api/search/barcode/3017624010701"
```

### GET `/api/search/name`
Recherche des produits par nom

**Paramètres:**
- `q` (string): Terme de recherche

**Exemple:**
```bash
curl "http://localhost:5000/api/search/name?q=nutella"
```

### POST `/api/consumption/add`
Ajoute une consommation au journal

**Body (JSON):**
```json
{
  "barcode": "3017624010701",
  "quantity": 100
}
```

### GET `/api/daily-summary`
Récupère le résumé nutritionnel du jour

**Paramètres:**
- `age` (int): Âge de l'utilisateur
- `sex` (string): 'homme' ou 'femme'
- `date` (string, optionnel): Date au format YYYY-MM-DD

**Exemple:**
```bash
curl "http://localhost:5000/api/daily-summary?age=30&sex=homme"
```

### GET `/api/history`
Récupère l'historique des consommations

**Paramètres:**
- `days` (int, optionnel): Nombre de jours (défaut: 7)

**Exemple:**
```bash
curl "http://localhost:5000/api/history?days=30"
```

## 📱 Utilisation CLI (Ancien mode)

L'application en ligne de commande est toujours disponible:

```bash
python nutrition_app_python_final.py
```

## 🐛 Dépannage

### Erreur 403 de OpenFoodFacts
- L'API OpenFoodFacts peut limiter les requêtes
- Attendez quelques secondes entre les recherches
- Vérifiez votre connexion Internet

### Base de données verrouillée
```bash
rm nutrition_data.db
python web_app.py
```

### Port 5000 déjà utilisé
Modifiez le port dans `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 🤝 Contribution

Les contributions sont les bienvenues! Pour contribuer:

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est développé à des fins éducatives.

## 🙏 Remerciements

- **OpenFoodFacts** : Base de données collaborative de produits alimentaires
- **ANSES & EFSA** : Recommandations nutritionnelles officielles
- **Communauté Python & Flask** : Frameworks et outils

## 📞 Support

Pour toute question ou problème:
- Ouvrez une issue sur GitHub
- Consultez la documentation OpenFoodFacts: https://world.openfoodfacts.org/

---

Développé avec ❤️ pour votre santé et votre bien-être nutritionnel
