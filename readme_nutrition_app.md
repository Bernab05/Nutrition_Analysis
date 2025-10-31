# 🥗 Application d'Analyse Nutritionnelle - Documentation Technique Complète

> Application Python pour suivre et analyser votre consommation alimentaire quotidienne via l'API OpenFoodFacts

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenFoodFacts](https://img.shields.io/badge/API-OpenFoodFacts-orange.svg)](https://world.openfoodfacts.org/)

---

## 📑 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture du Projet](#architecture-du-projet)
3. [Installation](#installation)
4. [Guide d'Utilisation](#guide-dutilisation)
5. [Explication Détaillée du Code](#explication-détaillée-du-code)
6. [Structure de la Base de Données](#structure-de-la-base-de-données)
7. [API OpenFoodFacts](#api-openfoodfacts)
8. [Gestion des Erreurs](#gestion-des-erreurs)
9. [Exemples Avancés](#exemples-avancés)
10. [FAQ Technique](#faq-technique)

---

## 🎯 Vue d'Ensemble

### Description

Cette application permet aux utilisateurs de :
- **Rechercher** des produits alimentaires par code-barre ou nom
- **Analyser** les informations nutritionnelles détaillées (Nutri-Score, NOVA, Eco-Score)
- **Enregistrer** leurs consommations quotidiennes avec quantités personnalisées
- **Visualiser** des rapports nutritionnels journaliers (calories, macronutriments)
- **Consulter** l'historique complet de leurs consommations

### Fonctionnalités Principales

| Fonctionnalité | Description | Technologie |
|----------------|-------------|-------------|
| **Recherche produit** | Code-barre ou nom | API REST OpenFoodFacts |
| **Stockage local** | Historique persistant | SQLite3 |
| **Calculs nutritionnels** | Agrégations quotidiennes | SQL avec fonctions d'agrégation |
| **Interface CLI** | Menu interactif | Python standard (input/print) |
| **Gestion erreurs** | Retry, timeout, fallback | requests + try/except |

### Technologies Utilisées

```
Python 3.8+
├── requests (HTTP client)
├── sqlite3 (base de données)
├── dataclasses (modèles de données)
├── datetime (gestion dates)
└── typing (annotations de type)
```

---

## 🏗️ Architecture du Projet

### Diagramme de l'Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   InteractiveMenu                       │
│  (Interface utilisateur - Gestion du flux applicatif)  │
└──────────────┬──────────────────────────────────────────┘
               │
               ├─► NutritionAnalyzer (Orchestrateur)
               │   └─┬─► OpenFoodFactsAPI (Client HTTP)
               │     │   └─► API OpenFoodFacts (Externe)
               │     │
               │     └─► ConsumptionTracker (Gestionnaire BDD)
               │         └─► SQLite Database (nutrition_data.db)
               │
               └─► Product (Modèle de données)
```

### Flux de Données

```
1. Utilisateur saisit un code-barre
   ↓
2. InteractiveMenu → NutritionAnalyzer
   ↓
3. NutritionAnalyzer → OpenFoodFactsAPI
   ↓
4. OpenFoodFactsAPI → API REST (HTTP GET)
   ↓
5. API retourne JSON → Parsing vers Product
   ↓
6. Product → ConsumptionTracker → SQLite
   ↓
7. Confirmation → Utilisateur
```

### Organisation du Code (525 lignes)

| Lignes | Section | Responsabilité |
|--------|---------|----------------|
| 1-20 | Imports & Docstring | Configuration et documentation |
| 22-42 | Classe `Product` | Modèle de données (dataclass) |
| 45-145 | Classe `OpenFoodFactsAPI` | Communication avec l'API externe |
| 148-235 | Classe `ConsumptionTracker` | Gestion base de données SQLite |
| 238-310 | Classe `NutritionAnalyzer` | Orchestration et affichage |
| 313-520 | Classe `InteractiveMenu` | Interface utilisateur CLI |
| 523-525 | Point d'entrée | Lancement de l'application |

---

## 📦 Installation

### Prérequis

- **Python 3.8 ou supérieur**
- **Connexion internet** (pour l'API OpenFoodFacts)
- **pip** (gestionnaire de paquets Python)

### Installation Étape par Étape

```bash
# 1. Créer un dossier pour le projet
mkdir nutrition-analyzer
cd nutrition-analyzer

# 2. Créer le fichier Python
nano nutrition_app.py
# (Coller le code complet)

# 3. Installer la dépendance
pip install requests

# Alternative si problème
python -m pip install --upgrade pip
python -m pip install requests

# 4. Vérifier l'installation
python -c "import requests; print('✅ Requests installé')"

# 5. Lancer l'application
python nutrition_app.py
```

### Configuration Optionnelle

```python
# Pour changer le nom de la base de données
tracker = ConsumptionTracker(db_path="mes_donnees.db")

# Pour modifier les timeouts API
response = self.session.get(url, timeout=30)  # 30 secondes
```

---

## 📖 Guide d'Utilisation

### Lancement

```bash
python nutrition_app.py
```

### Menu Principal

```
============================================================
🥗 APPLICATION D'ANALYSE NUTRITIONNELLE
============================================================

📋 MENU PRINCIPAL

[1] ou [B] Rechercher par CODE-BARRE
[2] ou [N] Rechercher par NOM
[3] ou [A] Ajouter au journal
[4] ou [R] Voir le rapport du jour
[5] ou [H] Voir l'historique
[0] ou [Q] Quitter
```

### Exemples d'Utilisation

#### Exemple 1 : Rechercher Nutella

```
👉 Votre choix: 1
📱 Entrez le code-barre: 3017624010701

Résultat :
============================================================
📦 Nutella
🏷️  Marque: Ferrero
============================================================

📊 SCORES
  • Nutri-Score: E
  • Groupe NOVA: 4
  • Eco-Score: D

🍽️  POUR 100g
  • Énergie: 539 kcal
  • Protéines: 6.3 g
  • Glucides: 57.5 g
  • Lipides: 30.9 g
  • Fibres: 0.0 g
  • Sel: 0.107 g
```

#### Exemple 2 : Ajouter au Journal

```
👉 Votre choix: 3
📱 Code-barre du produit: 3017624010701
✅ Produit: Nutella
📏 Quantité en grammes: 50

✅ Consommation enregistrée: Nutella (50g)
```

#### Exemple 3 : Rapport du Jour

```
👉 Votre choix: 4

============================================================
📅 RAPPORT DU 2025-10-21
============================================================
🔢 Nombre de produits: 3
⚡ Énergie totale: 892.5 kcal
💪 Protéines: 28.4 g
🍚 Glucides: 102.3 g
🥑 Lipides: 35.7 g
============================================================
```

---

## 🔍 Explication Détaillée du Code

### 1. Classe `Product` (Modèle de Données)

```python
@dataclass
class Product:
    """Modèle de données produit"""
    barcode: str
    name: str
    brands: str
    nutriscore: Optional[str] = None
    # ... autres champs
```

**Explication :**
- **`@dataclass`** : Décorateur Python qui génère automatiquement `__init__`, `__repr__`, etc.
- **`Optional[str]`** : Annotation de type indiquant que le champ peut être `None`
- **Valeurs par défaut** : Certains champs ont `= None` car ils ne sont pas toujours disponibles

**Pourquoi une dataclass ?**
- ✅ **Concision** : Moins de code boilerplate
- ✅ **Type safety** : Vérification des types avec mypy
- ✅ **Immutabilité optionnelle** : Peut être rendu frozen
- ✅ **Sérialisation facile** : Méthode `to_dict()` pour JSON/SQL

**Méthode `to_dict()` :**

```python
def to_dict(self):
    return asdict(self)
```

Convertit l'objet Product en dictionnaire Python :
```python
product.to_dict()
# Retourne : {'barcode': '123', 'name': 'Nutella', ...}
```

---

### 2. Classe `OpenFoodFactsAPI` (Client HTTP)

#### 2.1 Initialisation avec Retry Strategy

```python
def __init__(self):
    self.session = requests.Session()
    self.session.headers.update({"User-Agent": self.USER_AGENT})
    
    # Configuration de retry automatique
    retry_strategy = Retry(
        total=3,              # 3 tentatives maximum
        backoff_factor=1,     # Délai exponentiel : 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504]
    )
```

**Explication technique :**

| Paramètre | Valeur | Signification |
|-----------|--------|---------------|
| `total=3` | 3 | Nombre de tentatives maximum |
| `backoff_factor=1` | 1s | Délai entre tentatives (exponentiel) |
| `status_forcelist` | [429, 500...] | Codes HTTP déclenchant un retry |

**Pourquoi un retry ?**
- 🌐 **Réseau instable** : Connexion peut être temporairement coupée
- ⚡ **Serveur surchargé** : 429 (Too Many Requests) → Réessayer après
- 🔧 **Erreurs transitoires** : 500, 502, 503 → Souvent résolus en quelques secondes

**Séquence de retry :**

```
Tentative 1 → Échec (timeout)
   ⏱️  Attendre 1 seconde
Tentative 2 → Échec (500)
   ⏱️  Attendre 2 secondes
Tentative 3 → Succès ✅
```

#### 2.2 Méthode `get_product()` - Récupération d'un Produit

```python
def get_product(self, barcode: str) -> Optional[Product]:
    url = f"{self.BASE_URL}/product/{barcode}"
    params = {
        "fields": "product_name,brands,nutrition_grades,..."
    }
    
    try:
        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != 1:
            return None
        
        return self._parse_product(barcode, data["product"])
    except requests.exceptions.Timeout:
        print("⏱️  Timeout...")
        return None
```

**Décomposition étape par étape :**

**Étape 1 : Construction de l'URL**
```python
url = f"{self.BASE_URL}/product/{barcode}"
# Exemple : https://world.openfoodfacts.net/api/v2/product/3017624010701
```

**Étape 2 : Paramètres de requête**
```python
params = {"fields": "product_name,brands,..."}
# Limite les données retournées (optimisation bande passante)
```

**Étape 3 : Requête HTTP GET**
```python
response = self.session.get(url, params=params, timeout=20)
# Timeout de 20 secondes → Évite blocage indéfini
```

**Étape 4 : Vérification du statut HTTP**
```python
response.raise_for_status()
# Lance une exception si code != 2xx (200, 201, etc.)
```

**Étape 5 : Parsing JSON**
```python
data = response.json()
# Convertit le JSON en dictionnaire Python
```

**Étape 6 : Vérification métier**
```python
if data.get("status") != 1:
    return None
# OpenFoodFacts retourne status=1 si produit trouvé
```

**Gestion des exceptions :**

| Exception | Cause | Action |
|-----------|-------|--------|
| `Timeout` | Serveur trop lent | Message + return None |
| `ConnectionError` | Pas de connexion | Message + return None |
| `HTTPError` | Code 4xx/5xx | Message + return None |
| `JSONDecodeError` | Réponse invalide | Capturé par `RequestException` |

#### 2.3 Méthode `_parse_product()` - Transformation des Données

```python
def _parse_product(self, barcode: str, data: Dict) -> Product:
    nutriments = data.get("nutriments", {})
    
    return Product(
        barcode=barcode,
        name=data.get("product_name", "Inconnu"),
        brands=data.get("brands", ""),
        nutriscore=data.get("nutrition_grades", "").upper(),
        energy_kcal=nutriments.get("energy-kcal_100g"),
        # ...
    )
```

**Explication des choix de design :**

**1. Utilisation de `.get()` avec valeurs par défaut**
```python
data.get("product_name", "Inconnu")
# Si la clé n'existe pas → Retourne "Inconnu" au lieu de lever KeyError
```

**2. Transformation des données**
```python
nutrition_grades.upper()  # "e" → "E"
# Normalisation pour cohérence visuelle
```

**3. Navigation dans le JSON imbriqué**
```python
nutriments = data.get("nutriments", {})
nutriments.get("energy-kcal_100g")
# Évite : data["nutriments"]["energy-kcal_100g"]
# Qui crasherait si "nutriments" n'existe pas
```

**Structure JSON OpenFoodFacts (simplifié) :**

```json
{
  "status": 1,
  "product": {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "nutrition_grades": "e",
    "nova_group": 4,
    "nutriments": {
      "energy-kcal_100g": 539,
      "proteins_100g": 6.3,
      "carbohydrates_100g": 57.5,
      "fat_100g": 30.9
    },
    "allergens_tags": ["en:milk", "en:nuts"]
  }
}
```

#### 2.4 Méthode `search_products()` - Recherche par Nom

```python
def search_products(self, query: str, page_size: int = 20) -> List[Dict]:
    url = f"{self.SEARCH_URL}/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": min(page_size, 100)
    }
```

**Paramètres de l'API de recherche :**

| Paramètre | Valeur | Rôle |
|-----------|--------|------|
| `search_terms` | "nutella" | Mots-clés de recherche |
| `search_simple` | 1 | Mode recherche simplifiée |
| `action` | "process" | Déclenche le traitement |
| `json` | 1 | Format de réponse JSON |
| `page_size` | 20 | Nombre de résultats |

**Pourquoi `min(page_size, 100)` ?**
```python
min(page_size, 100)
# Limite à 100 même si utilisateur demande 1000
# Protection contre abus et respect des limites API
```

**Méthode de fallback `_search_alternative()` :**

```python
def _search_alternative(self, query: str, page_size: int = 20):
    # Si recherche principale échoue, essayer par marque
    params = {
        "brands_tags": query.lower().replace(" ", "-")
    }
```

**Stratégie de fallback en cascade :**

```
1. Tentative : Recherche textuelle complète
   ↓ (si échec)
2. Tentative : Recherche par marque
   ↓ (si échec)
3. Retour : Liste vide []
```

---

### 3. Classe `ConsumptionTracker` (Gestion Base de Données)

#### 3.1 Initialisation et Création de la Table

```python
def __init__(self, db_path: str = "nutrition_data.db"):
    self.db_path = Path(db_path)
    self._init_database()

def _init_database(self):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            product_name TEXT,
            quantity REAL DEFAULT 100,
            unit TEXT DEFAULT 'g',
            timestamp TEXT NOT NULL,
            nutriscore TEXT,
            energy_kcal REAL,
            proteins REAL,
            carbohydrates REAL,
            fat REAL
        )
    """)
```

**Explication SQL détaillée :**

| Colonne | Type | Contraintes | Rôle |
|---------|------|-------------|------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identifiant unique |
| `barcode` | TEXT | NOT NULL | Code-barre du produit |
| `product_name` | TEXT | - | Nom du produit |
| `quantity` | REAL | DEFAULT 100 | Quantité consommée |
| `unit` | TEXT | DEFAULT 'g' | Unité de mesure |
| `timestamp` | TEXT | NOT NULL | Date/heure ISO 8601 |
| `nutriscore` | TEXT | - | Score A-E |
| `energy_kcal` | REAL | - | Calories pour 100g |
| `proteins` | REAL | - | Protéines pour 100g |
| `carbohydrates` | REAL | - | Glucides pour 100g |
| `fat` | REAL | - | Lipides pour 100g |

**Pourquoi `CREATE TABLE IF NOT EXISTS` ?**
```sql
CREATE TABLE IF NOT EXISTS consumption (...)
-- Ne crée la table que si elle n'existe pas déjà
-- Évite les erreurs au lancement répété de l'app
```

**Pourquoi stocker `energy_kcal` pour 100g ?**
- ✅ **Cohérence** : Toutes les valeurs sont pour 100g
- ✅ **Calculs faciles** : `(energy_kcal * quantity) / 100`
- ✅ **Espace optimisé** : Pas besoin de recalculer

**Pattern de connexion SQLite :**

```python
conn = sqlite3.connect(self.db_path)  # Ouvrir
cursor = conn.cursor()                # Créer curseur
cursor.execute(...)                   # Exécuter requête
conn.commit()                         # Valider transaction
conn.close()                          # Fermer connexion
```

#### 3.2 Méthode `add_consumption()` - Insertion de Données

```python
def add_consumption(self, product: Product, quantity: float = 100, unit: str = "g"):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO consumption 
        (barcode, product_name, quantity, unit, timestamp, nutriscore, 
         energy_kcal, proteins, carbohydrates, fat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product.barcode,
        product.name,
        quantity,
        unit,
        datetime.now().isoformat(),
        product.nutriscore,
        product.energy_kcal,
        product.proteins,
        product.carbohydrates,
        product.fat
    ))
```

**Requête SQL paramétrée :**

**❌ MAUVAIS (Injection SQL) :**
```python
cursor.execute(f"INSERT INTO consumption VALUES ({product.barcode}, ...)")
# Vulnérable aux attaques par injection SQL !
```

**✅ BON (Paramètres liés) :**
```python
cursor.execute("INSERT INTO ... VALUES (?, ?, ?)", (val1, val2, val3))
# Les '?' sont remplacés par les valeurs de manière sécurisée
```

**Format de timestamp ISO 8601 :**
```python
datetime.now().isoformat()
# Retourne : "2025-10-21T14:30:45.123456"
# Avantages :
# - Standard international
# - Triable alphabétiquement
# - Compatible SQLite DATE()
```

**Transaction SQLite :**

```
BEGIN TRANSACTION (implicite)
   ↓
INSERT INTO consumption ...
   ↓
conn.commit()  ← Validation
   ↓
Données persistées sur disque ✅
```

**Si erreur avant commit :**
```
BEGIN TRANSACTION
   ↓
INSERT INTO consumption ...
   ↓
Exception levée ❌
   ↓
ROLLBACK (automatique)
   ↓
Aucune donnée enregistrée
```

#### 3.3 Méthode `get_daily_summary()` - Agrégations SQL

```python
def get_daily_summary(self, date: Optional[str] = None) -> Dict:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT 
            SUM(energy_kcal * quantity / 100) as total_kcal,
            SUM(proteins * quantity / 100) as total_proteins,
            SUM(carbohydrates * quantity / 100) as total_carbs,
            SUM(fat * quantity / 100) as total_fat,
            COUNT(*) as num_products
        FROM consumption
        WHERE DATE(timestamp) = ?
    """, (date,))
```

**Explication SQL avancée :**

**1. Fonctions d'agrégation :**

| Fonction | Description | Exemple |
|----------|-------------|---------|
| `SUM()` | Somme des valeurs | `SUM(energy_kcal)` |
| `COUNT()` | Nombre de lignes | `COUNT(*)` |
| `AVG()` | Moyenne | `AVG(quantity)` |
| `MIN()` | Minimum | `MIN(timestamp)` |
| `MAX()` | Maximum | `MAX(energy_kcal)` |

**2. Calcul des calories consommées :**

```sql
SUM(energy_kcal * quantity / 100)
```

**Décomposition mathématique :**

```
Produit 1 : 539 kcal/100g × 50g / 100 = 269.5 kcal
Produit 2 : 200 kcal/100g × 150g / 100 = 300 kcal
Produit 3 : 100 kcal/100g × 200g / 100 = 200 kcal
                                         ─────────
                              SUM() =    769.5 kcal
```

**3. Fonction `DATE()` :**

```sql
WHERE DATE(timestamp) = ?
```

**Exemple pratique :**

```sql
timestamp = "2025-10-21T14:30:45"
DATE(timestamp) = "2025-10-21"

-- Compare uniquement la date, ignore l'heure
```

**4. Résultat de la requête :**

```python
result = cursor.fetchone()
# Retourne : (769.5, 28.4, 102.3, 35.7, 3)
#            ↑      ↑     ↑      ↑     ↑
#            kcal   prot  carbs  fat   count
```

**5. Construction du dictionnaire de retour :**

```python
return {
    "date": date,
    "total_kcal": round(result[0] or 0, 1),  # Arrondi à 1 décimale
    "total_proteins": round(result[1] or 0, 1),
    "total_carbs": round(result[2] or 0, 1),
    "total_fat": round(result[3] or 0, 1),
    "num_products": result[4]
}
```

**Pourquoi `result[0] or 0` ?**
```python
result[0] or 0
# Si result[0] est None → Retourne 0
# Si result[0] est 123.45 → Retourne 123.45
```

#### 3.4 Méthode `get_history()` - Récupération de l'Historique

```python
def get_history(self, days: int = 7) -> List[Dict]:
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row  # ← Important !
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM consumption
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
    """, (days,))
    
    results = [dict(row) for row in cursor.fetchall()]
```

**`sqlite3.Row` - Accès par nom de colonne :**

**Sans `row_factory` :**
```python
row = (1, "3017624010701", "Nutella", 100, "g", ...)
# Accès : row[0], row[1], row[2]
# ❌ Difficile à lire
```

**Avec `row_factory` :**
```python
row = sqlite3.Row(...)
# Accès : row['id'], row['barcode'], row['product_name']
# ✅ Lisible et maintenable
```

**Fonction SQLite `datetime()` avec modificateurs :**

```sql
datetime('now', '-7 days')
-- Retourne la date/heure d'il y a 7 jours
```

**Exemples de modificateurs :**

```sql
datetime('now', '-1 hour')    -- Il y a 1 heure
datetime('now', '+3 days')    -- Dans 3 jours
datetime('now', 'start of day')  -- Aujourd'hui à 00:00
datetime('now', 'start of month')  -- Premier jour du mois
```

**Concaténation SQL avec `||` :**

```sql
'-' || ? || ' days'
-- Si ? = 7
-- Résultat : '-7 days'
```

**List comprehension pour conversion :**

```python
results = [dict(row) for row in cursor.fetchall()]
# Convertit chaque Row en dictionnaire Python
```

**Équivalent explicite :**

```python
results = []
for row in cursor.fetchall():
    results.append(dict(row))
```

---

### 4. Classe `NutritionAnalyzer` (Orchestrateur)

```python
class NutritionAnalyzer:
    def __init__(self):
        self.api = OpenFoodFactsAPI()
        self.tracker = ConsumptionTracker()
```

**Pattern : Composition over Inheritance**

Cette classe **compose** deux autres classes plutôt que d'hériter :

```
NutritionAnalyzer
├── self.api (OpenFoodFactsAPI)
└── self.tracker (ConsumptionTracker)
```

**Avantages de la composition :**
- ✅ **Flexibilité** : Peut changer d'implémentation facilement
- ✅ **Testabilité** : Peut injecter des mocks
- ✅ **Séparation des responsabilités** : Chaque classe a un rôle clair

#### Méthode `analyze_product()` - Affichage Formaté

```python
def analyze_product(self, barcode: str) -> Optional[Product]:
    product = self.api.get_product(barcode)
    
    if not product:
        return None
    
    print(f"\n{'='*60}")
    print(f"📦 {product.name}")
    print(f"🏷️  Marque: {product.brands or 'Non renseigné'}")
    print(f"{'='*60}")
```

**Formatage avancé des strings :**

**1. f-strings (Python 3.6+) :**
```python
f"📦 {product.name}"
# Plus lisible que : "📦 " + product.name
```

**2. Multiplication de strings :**
```python
'='*60
# Retourne : "============...============" (60 fois)
```

**3. Opérateur `or` pour valeur par défaut :**
```python
product.brands or 'Non renseigné'
# Si product.brands est "", None, ou False → "Non renseigné"
# Sinon → valeur de product.brands
```

**4. Émojis dans le code :**
```python
print("📦")  # Code Unicode : U+1F4E6
# Fonctionne dans la plupart des terminaux modernes
```

---

### 5. Classe `InteractiveMenu` (Interface CLI)

#### 5.1 Test de Connectivité au Démarrage

```python
def _test_connectivity(self):
    try:
        start_time = time.time()
        
        response = requests.get(
            "https://world.openfoodfacts.net/api/v2/product/3017624010701",
            params={"fields": "code"},
            timeout=10
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ CONNEXION ÉTABLIE avec succès ({elapsed:.2f}s)")
```

**Mesure du temps de réponse :**

```python
start_time = time.time()  # Timestamp avant requête
# ... requête HTTP ...
elapsed = time.time() - start_time  # Temps écoulé en secondes

# Formatage : {elapsed:.2f}
# .2f = 2 décimales → 2.34567 devient "2.35"
```

**Pourquoi tester avec Nutella (3017624010701) ?**
- ✅ **Produit populaire** : Toujours présent dans la base
- ✅ **Réponse rapide** : Cache côté serveur
- ✅ **Fiable** : Unlikely to be deleted

#### 5.2 Gestion des Entrées Utilisateur avec Fallback

```python
def search_by_barcode(self):
    try:
        barcode = input("📱 Entrez le code-barre: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Annulé")
        return
```

**Gestion des exceptions d'entrée :**

| Exception | Cause | Comportement |
|-----------|-------|--------------|
| `EOFError` | Ctrl+D (Unix) ou Ctrl+Z (Windows) | Sortie propre |
| `KeyboardInterrupt` | Ctrl+C | Interruption utilisateur |

**Méthode `.strip()` :**
```python
"  3017624010701  ".strip()
# Retourne : "3017624010701"
# Supprime espaces avant et après
```

#### 5.3 Mapping des Choix - Pattern Dictionary

```python
choice_map = {
    '1': '1', 'B': '1',
    '2': '2', 'N': '2',
    '3': '3', 'A': '3',
    '4': '4', 'R': '4',
    '5': '5', 'H': '5',
    '0': '0', 'Q': '0', 'QUIT': '0', 'EXIT': '0'
}

choice = choice_map.get(choice, choice)
```

**Avantages de ce pattern :**

**Au lieu de :**
```python
if choice == '1' or choice == 'B':
    action1()
elif choice == '2' or choice == 'N':
    action2()
# ... répétitif et verbeux
```

**On a :**
```python
choice = choice_map.get(choice, choice)  # Normalisation
if choice == '1':
    action1()
# ... simple et clair
```

**`.get()` avec valeur par défaut :**
```python
choice_map.get('X', 'X')
# Si 'X' n'est pas dans le dictionnaire → Retourne 'X'
# Évite KeyError
```

---

## 🗄️ Structure de la Base de Données

### Schéma Complet

```sql
CREATE TABLE consumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT NOT NULL,
    product_name TEXT,
    quantity REAL DEFAULT 100,
    unit TEXT DEFAULT 'g',
    timestamp TEXT NOT NULL,
    nutriscore TEXT,
    energy_kcal REAL,
    proteins REAL,
    carbohydrates REAL,
    fat REAL
);
```

### Exemples de Données

| id | barcode | product_name | quantity | unit | timestamp | nutriscore | energy_kcal | proteins | carbohydrates | fat |
|----|---------|--------------|----------|------|-----------|------------|-------------|----------|---------------|-----|
| 1 | 3017624010701 | Nutella | 50.0 | g | 2025-10-21T08:30:00 | E | 539.0 | 6.3 | 57.5 | 30.9 |
| 2 | 5449000000996 | Coca-Cola | 330.0 | ml | 2025-10-21T12:15:00 | E | 42.0 | 0.0 | 10.6 | 0.0 |
| 3 | 3168930010883 | Activia | 125.0 | g | 2025-10-21T19:00:00 | B | 73.0 | 4.0 | 11.0 | 1.5 |

### Requêtes SQL Utiles

#### Statistiques Globales

```sql
-- Total de calories consommées sur tous les temps
SELECT SUM(energy_kcal * quantity / 100) as total_kcal
FROM consumption;

-- Produit le plus consommé
SELECT product_name, COUNT(*) as count
FROM consumption
GROUP BY product_name
ORDER BY count DESC
LIMIT 1;

-- Moyenne de calories par jour
SELECT 
    DATE(timestamp) as date,
    SUM(energy_kcal * quantity / 100) as daily_kcal
FROM consumption
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

#### Analyse par Nutri-Score

```sql
-- Répartition par Nutri-Score
SELECT 
    nutriscore,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM consumption), 1) as percentage
FROM consumption
WHERE nutriscore IS NOT NULL
GROUP BY nutriscore
ORDER BY nutriscore;
```

#### Historique Hebdomadaire

```sql
-- Derniers 7 jours avec totaux quotidiens
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as products,
    ROUND(SUM(energy_kcal * quantity / 100), 1) as kcal,
    ROUND(SUM(proteins * quantity / 100), 1) as proteins
FROM consumption
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Maintenance de la Base

#### Sauvegarder les Données

```bash
# Dump SQL
sqlite3 nutrition_data.db .dump > backup.sql

# Export CSV
sqlite3 -header -csv nutrition_data.db "SELECT * FROM consumption;" > export.csv
```

#### Restaurer une Sauvegarde

```bash
# Depuis un dump SQL
sqlite3 nutrition_data.db < backup.sql

# Créer une nouvelle base depuis CSV
sqlite3 new_db.db
.mode csv
.import export.csv consumption
```

#### Nettoyer les Anciennes Données

```sql
-- Supprimer les entrées de plus de 6 mois
DELETE FROM consumption
WHERE timestamp < datetime('now', '-6 months');

-- Vacuum pour récupérer l'espace disque
VACUUM;
```

---

## 🌐 API OpenFoodFacts

### Documentation Officielle

- **Base URL** : `https://world.openfoodfacts.net`
- **Version API** : v2
- **Format** : JSON
- **Rate Limits** : 
  - 100 req/min pour lecture produits
  - 10 req/min pour recherche
  - 2 req/min pour requêtes facettes

### Endpoints Utilisés

#### 1. Récupération d'un Produit

**URL :** `GET /api/v2/product/{barcode}`

**Exemple :**
```
https://world.openfoodfacts.net/api/v2/product/3017624010701
```

**Paramètres de requête :**
- `fields` : Champs à retourner (séparés par virgules)

**Réponse (structure simplifiée) :**
```json
{
  "status": 1,
  "status_verbose": "product found",
  "product": {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "nutrition_grades": "e",
    "nova_group": 4,
    "ecoscore_grade": "d",
    "nutriments": {
      "energy-kcal_100g": 539,
      "proteins_100g": 6.3,
      "carbohydrates_100g": 57.5,
      "fat_100g": 30.9,
      "fiber_100g": 0,
      "salt_100g": 0.107
    },
    "allergens_tags": ["en:milk", "en:nuts"]
  }
}
```

#### 2. Recherche de Produits

**URL :** `GET /cgi/search.pl`

**Paramètres :**
- `search_terms` : Mots-clés
- `search_simple` : 1 (mode simple)
- `action` : "process"
- `json` : 1 (format JSON)
- `page_size` : Nombre de résultats

**Exemple :**
```
https://world.openfoodfacts.net/cgi/search.pl?search_terms=yaourt&search_simple=1&action=process&json=1&page_size=20
```

**Réponse :**
```json
{
  "count": 1234,
  "page": 1,
  "page_size": 20,
  "products": [
    {
      "code": "3168930010883",
      "product_name": "Activia Nature",
      "brands": "Danone",
      "nutrition_grades": "b"
    },
    // ... 19 autres produits
  ]
}
```

### Scores Disponibles

#### Nutri-Score (A-E)

| Score | Signification | Couleur |
|-------|---------------|---------|
| A | Très bonne qualité nutritionnelle | Vert foncé |
| B | Bonne qualité nutritionnelle | Vert clair |
| C | Qualité nutritionnelle moyenne | Jaune |
| D | Faible qualité nutritionnelle | Orange |
| E | Très faible qualité nutritionnelle | Rouge |

**Calcul** : Basé sur énergie, sucres, graisses saturées, sel, fruits/légumes, fibres, protéines

#### Groupe NOVA (1-4)

| Groupe | Signification |
|--------|---------------|
| 1 | Aliments non transformés ou minimalement transformés |
| 2 | Ingrédients culinaires transformés |
| 3 | Aliments transformés |
| 4 | Aliments ultra-transformés |

#### Eco-Score (A-E)

Évaluation de l'impact environnemental basée sur :
- Analyse du cycle de vie
- Empreinte carbone
- Origine des ingrédients
- Emballage

---

## ⚠️ Gestion des Erreurs

### Stratégie Globale

```
Erreur détectée
    ↓
1. Log/affichage du message d'erreur
    ↓
2. Tentative de récupération (retry, fallback)
    ↓
3. Si échec : retour gracieux (None, [], {})
    ↓
4. L'application continue de fonctionner
```

### Hiérarchie des Exceptions Requests

```
RequestException (base)
├── ConnectionError
│   ├── ConnectTimeout
│   └── ReadTimeout
├── HTTPError (4xx, 5xx)
├── Timeout
│   ├── ConnectTimeout
│   └── ReadTimeout
└── TooManyRedirects
```

### Gestion par Type d'Erreur

| Type d'Erreur | Détection | Action | Code |
|---------------|-----------|--------|------|
| **Timeout** | `requests.exceptions.Timeout` | Message + retry | `timeout=20` |
| **Pas de connexion** | `ConnectionError` | Message utilisateur | try/except |
| **404 Not Found** | `response.status_code == 404` | Message "non trouvé" | `raise_for_status()` |
| **500 Server Error** | `response.status_code >= 500` | Retry automatique | `Retry(status_forcelist=[500...])` |
| **JSON invalide** | `JSONDecodeError` | Capturé par `RequestException` | try/except |
| **Produit non trouvé** | `data['status'] != 1` | return None | Vérification métier |

### Exemples de Code de Gestion

#### Pattern Try-Except Complet

```python
try:
    # Code principal
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
    
except requests.exceptions.Timeout:
    # Timeout spécifique
    print("⏱️  Le serveur met trop de temps à répondre")
    return None
    
except requests.exceptions.ConnectionError:
    # Pas de connexion internet
    print("❌ Vérifiez votre connexion internet")
    return None
    
except requests.exceptions.HTTPError as e:
    # Erreur HTTP (4xx, 5xx)
    print(f"❌ Erreur serveur: {e.response.status_code}")
    return None
    
except requests.exceptions.RequestException as e:
    # Toute autre erreur requests
    print(f"❌ Erreur réseau: {e}")
    return None
    
except Exception as e:
    # Erreur inattendue
    print(f"❌ Erreur inattendue: {type(e).__name__}")
    return None
```

#### Pattern Input avec EOFError

```python
try:
    user_input = input("Votre choix: ").strip()
except (EOFError, KeyboardInterrupt):
    print("\n❌ Annulé")
    return
except Exception:
    print("❌ Erreur de lecture")
    time.sleep(1)
    return
```

---

## 💡 Exemples Avancés

### Exemple 1 : Script de Migration de Données

```python
"""
Migration des données d'une ancienne structure vers la nouvelle
"""
import sqlite3
from pathlib import Path

def migrate_database(old_db: str, new_db: str):
    old_conn = sqlite3.connect(old_db)
    new_conn = sqlite3.connect(new_db)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Créer la nouvelle table
    new_cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            product_name TEXT,
            quantity REAL DEFAULT 100,
            unit TEXT DEFAULT 'g',
            timestamp TEXT NOT NULL,
            nutriscore TEXT,
            energy_kcal REAL,
            proteins REAL,
            carbohydrates REAL,
            fat REAL
        )
    """)
    
    # Migrer les données
    old_cursor.execute("SELECT * FROM old_consumption")
    rows = old_cursor.fetchall()
    
    for row in rows:
        new_cursor.execute("""
            INSERT INTO consumption 
            (barcode, product_name, quantity, timestamp, energy_kcal)
            VALUES (?, ?, ?, ?, ?)
        """, (row[0], row[1], row[2], row[3], row[4]))
    
    new_conn.commit()
    
    print(f"✅ Migration terminée : {len(rows)} entrées")
    
    old_conn.close()
    new_conn.close()

if __name__ == "__main__":
    migrate_database("old_data.db", "nutrition_data.db")
```

### Exemple 2 : Export Vers Excel

```python
"""
Export des données nutrition vers Excel
Nécessite : pip install openpyxl
"""
import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from datetime import datetime

def export_to_excel(db_path: str = "nutrition_data.db", output_file: str = "export.xlsx"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            DATE(timestamp) as date,
            product_name,
            brands,
            quantity,
            unit,
            ROUND(energy_kcal * quantity / 100, 1) as consumed_kcal,
            nutriscore
        FROM consumption
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    
    # Créer workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Historique Nutrition"
    
    # En-têtes
    headers = ["Date", "Produit", "Marque", "Quantité", "Unité", "Calories", "Nutri-Score"]
    ws.append(headers)
    
    # Styliser les en-têtes
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    
    # Données
    for row in rows:
        ws.append([
            row['date'],
            row['product_name'],
            row['brands'],
            row['quantity'],
            row['unit'],
            row['consumed_kcal'],
            row['nutriscore']
        ])
    
    # Auto-ajuster les colonnes
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Sauvegarder
    wb.save(output_file)
    
    print(f"✅ Export terminé : {output_file} ({len(rows)} entrées)")
    
    conn.close()

if __name__ == "__main__":
    export_to_excel()
```

### Exemple 3 : Analyse Statistique Avancée

```python
"""
Analyse statistique des habitudes alimentaires
"""
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

class NutritionStats:
    def __init__(self, db_path: str = "nutrition_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def average_daily_calories(self, days: int = 30) -> float:
        """Moyenne de calories par jour sur N jours"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                SUM(energy_kcal * quantity / 100) as daily_kcal
            FROM consumption
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
        """, (days,))
        
        daily_totals = [row['daily_kcal'] for row in cursor.fetchall()]
        
        if not daily_totals:
            return 0.0
        
        return sum(daily_totals) / len(daily_totals)
    
    def most_consumed_products(self, limit: int = 10) -> list:
        """Top N produits les plus consommés"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                product_name,
                COUNT(*) as count,
                SUM(quantity) as total_quantity,
                ROUND(SUM(energy_kcal * quantity / 100), 1) as total_kcal
            FROM consumption
            GROUP BY product_name
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def nutriscore_distribution(self) -> dict:
        """Répartition par Nutri-Score"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                nutriscore,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM consumption), 1) as percentage
            FROM consumption
            WHERE nutriscore IS NOT NULL
            GROUP BY nutriscore
            ORDER BY nutriscore
        """)
        
        return {row['nutriscore']: row['percentage'] for row in cursor.fetchall()}
    
    def weekly_trends(self, weeks: int = 4) -> dict:
        """Tendances hebdomadaires"""
        cursor = self.conn.cursor()
        
        trends = defaultdict(list)
        
        for week in range(weeks):
            start_date = (datetime.now() - timedelta(weeks=week+1)).strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(weeks=week)).strftime("%Y-%m-%d")
            
            cursor.execute("""
                SELECT 
                    SUM(energy_kcal * quantity / 100) as total_kcal,
                    SUM(proteins * quantity / 100) as total_proteins
                FROM consumption
                WHERE DATE(timestamp) BETWEEN ? AND ?
            """, (start_date, end_date))
            
            row = cursor.fetchone()
            trends['calories'].append(row['total_kcal'] or 0)
            trends['proteins'].append(row['total_proteins'] or 0)
        
        return dict(trends)
    
    def print_report(self):
        """Afficher un rapport complet"""
        print("\n" + "="*60)
        print("📊 RAPPORT STATISTIQUE")
        print("="*60)
        
        # Moyenne calories
        avg_kcal = self.average_daily_calories(30)
        print(f"\n⚡ Moyenne quotidienne (30 jours): {avg_kcal:.1f} kcal")
        
        # Top produits
        print("\n🏆 TOP 5 PRODUITS:")
        for i, product in enumerate(self.most_consumed_products(5), 1):
            print(f"  {i}. {product['product_name']}")
            print(f"     • {product['count']} fois - {product['total_kcal']} kcal")
        
        # Distribution Nutri-Score
        print("\n📊 RÉPARTITION NUTRI-SCORE:")
        distribution = self.nutriscore_distribution()
        for score, percentage in distribution.items():
            print(f"  {score}: {percentage}%")
        
        print("\n" + "="*60)
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    stats = NutritionStats()
    stats.print_report()
```

---

## ❓ FAQ Technique

### Installation

**Q : J'ai l'erreur "requests module not found"**

```bash
# Solution 1
pip install requests

# Solution 2
python -m pip install requests

# Solution 3 (avec droits admin)
sudo pip install requests  # Linux/Mac
pip install --user requests  # Sans sudo
```

**Q : Comment installer une version spécifique de requests ?**

```bash
pip install requests==2.31.0
```

### Base de Données

**Q : Où est stockée la base de données ?**

```python
from pathlib import Path
import os

db_path = Path("nutrition_data.db")
print(f"Chemin absolu : {db_path.absolute()}")
print(f"Existe : {db_path.exists()}")
print(f"Taille : {os.path.getsize(db_path)} bytes")
```

**Q : Comment réinitialiser la base de données ?**

```bash
# Supprimer le fichier
rm nutrition_data.db

# Ou renommer
mv nutrition_data.db nutrition_data_backup.db

# L'app créera une nouvelle base au prochain lancement
```

**Q : La base de données est corrompue, comment réparer ?**

```bash
# Dump SQL
sqlite3 nutrition_data.db ".dump" > backup.sql

# Créer nouvelle base
sqlite3 new_nutrition_data.db < backup.sql

# Remplacer l'ancienne
mv new_nutrition_data.db nutrition_data.db
```

### API OpenFoodFacts

**Q : L'API retourne toujours timeout**

**Causes possibles :**
1. Serveur OpenFoodFacts surchargé → Réessayer plus tard
2. Connexion internet lente → Augmenter timeout
3. Firewall/proxy → Vérifier configuration réseau

**Solutions :**
```python
# Augmenter timeout
response = self.session.get(url, timeout=60)  # 60 secondes

# Tester connectivité
curl -w "@-" "https://world.openfoodfacts.net/api/v2/product/3017624010701"
```

**Q : Comment obtenir plus de champs dans la réponse ?**

```python
params = {
    "fields": "product_name,brands,categories,ingredients_text,image_url,nutriscore_data"
}
```

Liste complète des champs : https://world.openfoodfacts.org/data/data-fields.txt

### Performance

**Q : Comment accélérer les recherches ?**

**1. Implémenter un cache local :**
```python
import functools
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=128)
def get_product_cached(barcode: str) -> Product:
    return get_product(barcode)
```

**2. Pré-charger les produits fréquents :**
```python
FREQUENT_PRODUCTS = ["3017624010701", "5449000000996", ...]

for barcode in FREQUENT_PRODUCTS:
    get_product(barcode)  # Met en cache
```

**3. Utiliser des requêtes SQL optimisées :**
```sql
-- Créer un index
CREATE INDEX idx_timestamp ON consumption(timestamp);
CREATE INDEX idx_barcode ON consumption(barcode);
```

### Développement

**Q : Comment ajouter un nouveau champ dans Product ?**

```python
@dataclass
class Product:
    # ... champs existants ...
    
    # Nouveau champ
    serving_size: Optional[str] = None  # Ex: "25g"
```

Puis mettre à jour `_parse_product()` :
```python
serving_size=data.get("serving_size")
```

**Q : Comment ajouter une colonne dans la base ?**

```sql
ALTER TABLE consumption ADD COLUMN serving_size TEXT;
```

**Q : Comment créer des tests unitaires ?**

```python
import unittest
from unittest.mock import Mock, patch

class TestOpenFoodFactsAPI(unittest.TestCase):
    def setUp(self):
        self.api = OpenFoodFactsAPI()
    
    @patch('requests.Session.get')
    def test_get_product_success(self, mock_get):
        # Mock la réponse API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Test Product",
                "brands": "Test Brand"
            }
        }
        mock_get.return_value = mock_response
        
        # Test
        product = self.api.get_product("123")
        
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Test Product")
    
    def test_get_product_not_found(self):
        product = self.api.get_product("000")
        self.assertIsNone(product)

if __name__ == "__main__":
    unittest.main()
```

---

## 📚 Ressources Complémentaires

### Documentation

- **Python Requests** : https://requests.readthedocs.io/
- **SQLite3** : https://docs.python.org/3/library/sqlite3.html
- **OpenFoodFacts API** : https://openfoodfacts.github.io/openfoodfacts-server/api/
- **Dataclasses** : https://docs.python.org/3/library/dataclasses.html

### Outils Utiles

- **DB Browser for SQLite** : https://sqlitebrowser.org/
- **Postman** : Pour tester l'API OpenFoodFacts
- **VSCode** : Avec extensions Python et SQLite
- **Black** : Formateur de code Python

### Améliorations Futures

- [ ] Interface graphique (Tkinter/PyQt)
- [ ] Graphiques de tendances (matplotlib)
- [ ] Export PDF des rapports
- [ ] Synchronisation cloud
- [ ] Scanner de codes-barres (via webcam)
- [ ] Recommandations nutritionnelles IA
- [ ] Intégration avec balances connectées
- [ ] Mode multi-utilisateurs

---

## 📝 Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer.

---

## 👤 Auteur

Créé avec ❤️ pour l'éducation et la santé nutritionnelle.

Données fournies par [OpenFoodFacts](https://world.openfoodfacts.org/) - Base de données collaborative libre.

---

*Dernière mise à jour : Octobre 2025*