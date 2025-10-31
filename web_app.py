"""
Application Web d'Analyse Nutritionnelle - OpenFoodFacts
Interface web dynamique avec indicateurs d'apports journaliers recommandés

INSTALLATION:
pip install flask requests

UTILISATION:
python web_app.py
"""

from flask import Flask, render_template, request, jsonify
from nutrition_app_python_final import OpenFoodFactsAPI, ConsumptionTracker, Product
from datetime import datetime
from typing import Dict, Optional
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nutrition-analyzer-secret-key-2024'

# Initialisation des composants
api = OpenFoodFactsAPI()
tracker = ConsumptionTracker()


class NutritionalRecommendations:
    """
    Calcul des Apports Journaliers Recommandés (AJR) selon l'âge et le sexe
    Basé sur les recommandations de l'ANSES (France) et EFSA (Europe)
    """

    # Recommandations par profil (valeurs moyennes)
    RECOMMENDATIONS = {
        'homme': {
            '18-40': {
                'calories': 2500,
                'proteins': 70,      # g
                'carbohydrates': 310, # g
                'fat': 90,           # g
                'fiber': 30,         # g
                'salt': 6            # g (max)
            },
            '41-60': {
                'calories': 2350,
                'proteins': 65,
                'carbohydrates': 290,
                'fat': 85,
                'fiber': 30,
                'salt': 6
            },
            '61+': {
                'calories': 2150,
                'proteins': 70,      # augmenté pour seniors
                'carbohydrates': 265,
                'fat': 75,
                'fiber': 30,
                'salt': 5
            }
        },
        'femme': {
            '18-40': {
                'calories': 2000,
                'proteins': 55,
                'carbohydrates': 250,
                'fat': 70,
                'fiber': 25,
                'salt': 6
            },
            '41-60': {
                'calories': 1900,
                'proteins': 55,
                'carbohydrates': 235,
                'fat': 65,
                'fiber': 25,
                'salt': 6
            },
            '61+': {
                'calories': 1800,
                'proteins': 60,      # augmenté pour seniors
                'carbohydrates': 220,
                'fat': 60,
                'fiber': 25,
                'salt': 5
            }
        }
    }

    @classmethod
    def get_recommendations(cls, age: int, sex: str) -> Dict:
        """Retourne les recommandations pour un profil donné"""
        sex = sex.lower()

        if sex not in cls.RECOMMENDATIONS:
            sex = 'homme'  # valeur par défaut

        # Détermination de la tranche d'âge
        if age < 18:
            age_group = '18-40'  # utiliser les valeurs adultes pour simplifier
        elif age <= 40:
            age_group = '18-40'
        elif age <= 60:
            age_group = '41-60'
        else:
            age_group = '61+'

        recommendations = cls.RECOMMENDATIONS[sex][age_group].copy()
        recommendations['age_group'] = age_group
        recommendations['sex'] = sex

        return recommendations


@app.route('/')
def index():
    """Page d'accueil de l'application"""
    return render_template('index.html')


@app.route('/api/search/barcode/<barcode>')
def search_barcode(barcode):
    """Recherche un produit par code-barre"""
    try:
        product = api.get_product(barcode)

        if not product:
            return jsonify({
                'success': False,
                'message': f'Produit {barcode} non trouvé'
            }), 404

        return jsonify({
            'success': True,
            'product': product.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500


@app.route('/api/search/name')
def search_by_name():
    """Recherche des produits par nom"""
    query = request.args.get('q', '')

    if not query:
        return jsonify({
            'success': False,
            'message': 'Aucun terme de recherche fourni'
        }), 400

    try:
        results = api.search_products(query, page_size=10)

        # Formater les résultats
        products = []
        for product in results:
            products.append({
                'code': product.get('code'),
                'name': product.get('product_name', 'N/A'),
                'brands': product.get('brands', 'N/A'),
                'nutriscore': product.get('nutrition_grades', '').upper()
            })

        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500


@app.route('/api/consumption/add', methods=['POST'])
def add_consumption():
    """Ajoute une consommation au journal"""
    try:
        data = request.get_json()
        barcode = data.get('barcode')
        quantity = float(data.get('quantity', 100))

        if not barcode:
            return jsonify({
                'success': False,
                'message': 'Code-barre manquant'
            }), 400

        # Récupérer le produit
        product = api.get_product(barcode)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Produit non trouvé'
            }), 404

        # Enregistrer la consommation
        tracker.add_consumption(product, quantity)

        return jsonify({
            'success': True,
            'message': f'Consommation enregistrée: {product.name}',
            'product': product.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500


@app.route('/api/daily-summary')
def get_daily_summary():
    """Récupère le résumé nutritionnel du jour avec comparaison aux AJR"""
    try:
        # Paramètres utilisateur
        age = int(request.args.get('age', 30))
        sex = request.args.get('sex', 'homme')
        date = request.args.get('date', None)

        # Obtenir le résumé du jour
        summary = tracker.get_daily_summary(date)

        # Obtenir les recommandations
        recommendations = NutritionalRecommendations.get_recommendations(age, sex)

        # Calculer les pourcentages
        percentages = {
            'calories': round((summary['total_kcal'] / recommendations['calories']) * 100, 1),
            'proteins': round((summary['total_proteins'] / recommendations['proteins']) * 100, 1),
            'carbohydrates': round((summary['total_carbs'] / recommendations['carbohydrates']) * 100, 1),
            'fat': round((summary['total_fat'] / recommendations['fat']) * 100, 1)
        }

        return jsonify({
            'success': True,
            'summary': summary,
            'recommendations': recommendations,
            'percentages': percentages,
            'user_profile': {
                'age': age,
                'sex': sex
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500


@app.route('/api/history')
def get_history():
    """Récupère l'historique des consommations"""
    try:
        days = int(request.args.get('days', 7))
        history = tracker.get_history(days)

        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500


@app.route('/api/recommendations')
def get_recommendations():
    """Retourne les recommandations nutritionnelles pour un profil"""
    try:
        age = int(request.args.get('age', 30))
        sex = request.args.get('sex', 'homme')

        recommendations = NutritionalRecommendations.get_recommendations(age, sex)

        return jsonify({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🍎 APPLICATION WEB D'ANALYSE NUTRITIONNELLE")
    print("="*70)
    print("📊 Alimenté par OpenFoodFacts (2.9M+ produits)")
    print("💪 Suivi des apports journaliers recommandés (AJR)")
    print("="*70)
    print("\n🌐 Serveur démarré sur: http://127.0.0.1:5000")
    print("📱 Ouvrez cette adresse dans votre navigateur\n")
    print("💡 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
