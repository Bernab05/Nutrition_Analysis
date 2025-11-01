# 🥗 Nutrition Analysis App (Streamlit)

Cette application Streamlit vous permet d'analyser vos consommations alimentaires grâce à l'API OpenFoodFacts. Elle offre la recherche de produits, le suivi journalier et l'analyse détaillée de votre alimentation, avec comparaison aux apports journaliers recommandés (AJR).

---

## Fonctionnalités principales

- **Recherche de produits** :
  - Par code-barre (scan ou saisie manuelle)
  - Par nom ou marque
- **Analyse nutritionnelle détaillée** :
  - Affichage des scores Nutri-Score, NOVA, Eco-Score
  - Tableaux nutritionnels dynamiques pour différentes quantités
  - Calcul et comparaison avec vos AJR personnalisés (âge, sexe)
- **Journal alimentaire** :
  - Ajoutez des produits à votre journal avec la quantité consommée
  - Visualisez vos apports journaliers (calories, protéines, glucides, lipides…)
  - Affichage sous forme de progression vers les AJR
  - Suppression facile des entrées ou d'une journée entière
- **Historique** :
  - Consultez toutes vos consommations sur plusieurs jours
  - Supprimez des entrées individuellement
- **Explications pédagogiques** sur Nutri-Score, NOVA, Eco-Score

---

## Installation

1. **Clonez le dépôt :**
   ```bash
   git clone https://github.com/Bernab05/Nutrition_Analysis.git
   cd Nutrition_Analysis
   ```

2. **Installez les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```
   > Les principales bibliothèques requises : `streamlit`, `requests`, `pandas`, etc.

3. **Lancez l'application :**
   ```bash
   streamlit run FoodappWeb.py
   ```

---

## Utilisation

- Naviguez via la barre latérale :
  - **Rechercher un produit** pour débuter une analyse.
  - **Rapport Journalier** pour visualiser vos apports quotidiens.
  - **Historique** pour revoir/supprimer vos consommations.
  - **À propos des Scores** pour mieux comprendre les indicateurs utilisés.
- Renseignez votre âge et sexe pour une personnalisation des AJR.

---

## Données & Confidentialité

- **Aucune donnée n'est envoyée à des tiers** : tout est stocké localement dans `nutrition_data.db`.
- Les données produits proviennent de l'API publique [OpenFoodFacts](https://world.openfoodfacts.org).

---

## Limites & Avertissements

- Cette application est à visée éducative et ne remplace pas un avis médical ou professionnel.
- Les valeurs nutritionnelles sont celles indiquées par les fabricants, leur exactitude ne peut être garantie.
- L'API OpenFoodFacts peut parfois être indisponible ou incomplète selon les produits.

---

## Auteurs & Licence

- Auteur : [Bernab05](https://github.com/Bernab05)
- Projet open source sous licence MIT. Contributions bienvenues !

---

## Captures d'écran

> Ajoutez ici des captures d'écran de l'application pour illustrer les différentes fonctionnalités.

---

## Remerciements

- [OpenFoodFacts](https://world.openfoodfacts.org) pour la base de données produits.
- [Streamlit](https://streamlit.io/) pour la simplicité du développement web.
