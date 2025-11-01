# app.py
# Interface web Streamlit pour l'analyseur nutritionnel
# Version 2.5 avec suppression (jour/entrée) et tableau de rapport détaillé

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd


# --- MODÈLE DE DONNÉES ---

@dataclass
class Product:
    """Modèle de données produit"""
    barcode: str
    name: str
    brands: str
    nutriscore: Optional[str] = None
    nova_group: Optional[int] = None
    ecoscore: Optional[str] = None
    energy_kcal: Optional[float] = None
    proteins: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    salt: Optional[float] = None
    ingredients: Optional[str] = None
    allergens: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)


# --- CLASSE API (Corrigée pour le cache) ---

class OpenFoodFactsAPI:
    """Client API OpenFoodFacts (adapté pour Streamlit)"""

    BASE_URL = "https://world.openfoodfacts.net/api/v2"
    SEARCH_URL = "https://world.openfoodfacts.net"
    USER_AGENT = "NutritionAnalyzerStreamlit/1.0 (Educational Project)"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

        try:
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        except Exception as e:
            st.warning(f"Impossible de configurer les 'retries' : {e}")

    @st.cache_data(ttl=3600)
    def get_product(_self, barcode: str) -> Optional[Dict]:  # Renvoie un Dict
        """Récupère les données d'un produit via son code-barre"""
        url = f"{_self.BASE_URL}/product/{barcode}"
        params = {
            "fields": "product_name,brands,nutrition_grades,nova_group,"
                      "ecoscore_grade,nutriments,ingredients_text,allergens_tags"
        }

        try:
            response = _self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != 1:
                st.error(f"❌ Produit {barcode} non trouvé dans la base OpenFoodFacts")
                return None

            product = _self._parse_product(barcode, data["product"])
            return product.to_dict()  # Convertit en dictionnaire sérialisable

        except requests.exceptions.Timeout:
            st.error(f"⏱️ Timeout - Le serveur met trop de temps à répondre")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erreur API: {e}")
            return None

    def _parse_product(self, barcode: str, data: Dict) -> Product:
        """Parse la réponse API vers objet Product (identique)"""
        nutriments = data.get("nutriments", {})

        return Product(
            barcode=barcode,
            name=data.get("product_name", "Inconnu"),
            brands=data.get("brands", ""),
            nutriscore=data.get("nutrition_grades", "").upper(),
            nova_group=data.get("nova_group"),
            ecoscore=data.get("ecoscore_grade", "").upper(),
            energy_kcal=nutriments.get("energy-kcal_100g"),
            proteins=nutriments.get("proteins_100g"),
            carbohydrates=nutriments.get("carbohydrates_100g"),
            fat=nutriments.get("fat_100g"),
            fiber=nutriments.get("fiber_100g"),
            salt=nutriments.get("salt_100g"),
            ingredients=data.get("ingredients_text"),
            allergens=data.get("allergens_tags", [])
        )

    @st.cache_data(ttl=3600)
    def search_products(_self, query: str, page_size: int = 20) -> List[Dict]:
        """Recherche produits par mots-clés (adapté)"""
        url = f"{_self.SEARCH_URL}/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": min(page_size, 100)
        }

        try:
            response = _self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])

            if products:
                return products

            return _self._search_alternative(query, page_size)

        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Timeout - Essai avec méthode alternative...")
            return _self.search_alternative(query, page_size)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erreur réseau: {e}")
            return _self._search_alternative(query, page_size)

    def _search_alternative(self, query: str, page_size: int = 20) -> List[Dict]:
        """Méthode alternative de recherche (identique)"""
        try:
            if query.isdigit() and len(query) >= 8:
                url = f"{self.BASE_URL}/search"
                params = {"code": query, "page_size": 1, "fields": "code,product_name,brands,nutrition_grades"}
            else:
                url = f"{self.BASE_URL}/search"
                params = {"page_size": min(page_size, 50), "fields": "code,product_name,brands,nutrition_grades",
                          "brands_tags": query.lower().replace(" ", "-")}

            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
        except:
            return []


# --- GESTION DE LA CONSOMMATION ---

class ConsumptionTracker:
    """Gestionnaire d'historique de consommation"""

    def __init__(self, db_path: str = "nutrition_data.db"):
        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self):
        """Initialise la base de données SQLite"""
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

        conn.commit()
        conn.close()

    def add_consumption(self, product: Product, quantity: float = 100, unit: str = "g"):
        """Enregistre une consommation"""
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

        conn.commit()
        conn.close()

    def get_daily_summary(self, date_str: Optional[str] = None) -> Dict:
        """Calcule le résumé nutritionnel d'une journée"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                SUM(energy_kcal * quantity / 100) as total_kcal,
                SUM(proteins * quantity / 100) as total_proteins,
                SUM(carbohydrates * quantity / 100) as total_carbs,
                SUM(fat * quantity / 100) as total_fat,
                COUNT(*) as num_products
            FROM consumption
            WHERE DATE(timestamp) = ?
        """, (date_str,))

        result = cursor.fetchone()
        conn.close()

        return {
            "date": date_str,
            "total_kcal": round(result[0] or 0, 1),
            "total_proteins": round(result[1] or 0, 1),
            "total_carbs": round(result[2] or 0, 1),
            "total_fat": round(result[3] or 0, 1),
            "num_products": result[4]
        }

    def get_history(self, days: int = 7) -> List[Dict]:
        """Récupère l'historique des N derniers jours"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # NOUVEAU : On récupère aussi l'ID
        cursor.execute("""
            SELECT id, barcode, product_name, quantity, unit, timestamp, 
                   nutriscore, energy_kcal
            FROM consumption
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """, (days,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    # --- NOUVELLES FONCTIONS DE SUPPRESSION ---

    def delete_consumption_entry(self, entry_id: int):
        """Supprime une entrée spécifique de la consommation par son ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consumption WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()

    def delete_daily_summary(self, date_str: str):
        """Supprime toutes les entrées pour une date donnée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consumption WHERE DATE(timestamp) = ?", (date_str,))
        conn.commit()
        conn.close()

    def get_daily_entries(self, date_str: str) -> List[Dict]:
        """Récupère les entrées détaillées d'une journée"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, product_name, quantity, unit, 
                   (energy_kcal * quantity / 100) as consumed_kcal
            FROM consumption
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
        """, (date_str,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results


# --- INITIALISATION GLOBALE (Mise en cache Streamlit) ---

@st.cache_resource
def get_api_client():
    return OpenFoodFactsAPI()


@st.cache_resource
def get_tracker():
    return ConsumptionTracker()


api = get_api_client()
tracker = get_tracker()


# --- GESTION DES AJR (Apports Journaliers Recommandés) ---

def get_rdi(age: Optional[int], sex: Optional[str]) -> Dict:
    """
    Estime les Apports Journaliers Recommandés (AJR)
    Source: Basé sur les moyennes des données ANSES (Agence nationale de sécurité sanitaire)
    """
    # Valeurs par défaut (Femme, 40-60 ans, activité moyenne)
    kcal = 2000.0

    if sex == 'Homme':
        if age and age < 40:
            kcal = 2700.0
        elif age and age <= 60:
            kcal = 2500.0
        elif age and age > 60:
            kcal = 2200.0  # Approximation
        else:
            kcal = 2600.0  # Homme générique
    elif sex == 'Femme':
        if age and age < 40:
            kcal = 2200.0
        elif age and age <= 60:
            kcal = 2000.0
        elif age and age > 60:
            kcal = 1800.0  # Approximation
        else:
            kcal = 2100.0  # Femme générique

    rdi = {
        'kcal': round(kcal, 0),
        'proteins': round((kcal * 0.15) / 4, 1),  # 1g prot = 4 kcal
        'fat': round((kcal * 0.375) / 9, 1),  # 1g lipide = 9 kcal
        'carbs': round((kcal * 0.475) / 4, 1),  # 1g glucide = 4 kcal
        'fiber': 30.0,
        'salt': 5.0  # Limite max recommandée
    }
    return rdi


# --- FONCTIONS D'AFFICHAGE ---

def display_product_details(product: Product):
    """
    Affiche les détails d'un produit dans Streamlit
    MAJ: Ajout de la quantité dynamique, affichage en tableau, et % AJR
    """
    st.header(f"📦 {product.name}")
    st.caption(f"**Marque :** {product.brands or 'Non renseigné'} | **Code-barre :** {product.barcode}")
    st.divider()

    st.subheader("📊 Scores")
    cols_scores = st.columns(3)
    cols_scores[0].metric("Nutri-Score", product.nutriscore or "N/A")
    cols_scores[1].metric("Groupe NOVA", str(product.nova_group) or "N/A")
    cols_scores[2].metric("Eco-Score", product.ecoscore or "N/A")

    st.divider()

    # --- Section Quantité Dynamique ---
    st.subheader("🍽️ Analyse Nutritionnelle")
    # Ce 'quantity' est local à cette fonction
    quantity = st.number_input(
        "Quantité (en grammes)",
        min_value=1.0,
        value=100.0,
        step=10.0,
        key=f"quantity_input_{product.barcode}"
    )

    # --- Calcul dynamique pour le tableau ---
    ratio = quantity / 100.0
    rdi = get_rdi(st.session_state.user_age, st.session_state.user_sex)

    def calculate_pct(nutrient_val, rdi_val):
        if nutrient_val is None or rdi_val is None or rdi_val == 0:
            return "N/A"
        pct = (nutrient_val / rdi_val) * 100
        return f"{pct:.1f}%"

    energy_port = product.energy_kcal * ratio if product.energy_kcal else None
    prot_port = product.proteins * ratio if product.proteins else None
    carbs_port = product.carbohydrates * ratio if product.carbohydrates else None
    fat_port = product.fat * ratio if product.fat else None
    fiber_port = product.fiber * ratio if product.fiber else None
    salt_port = product.salt * ratio if product.salt else None

    # --- Affichage en Tableau (avec % AJR) ---
    data = {
        "Composant": ["Énergie (kcal)", "Protéines (g)", "Glucides (g)", "Lipides (g)", "Fibres (g)", "Sel (g)"],
        "Pour 100g": [
            f"{product.energy_kcal:.1f}" if product.energy_kcal else "N/A",
            f"{product.proteins:.1f}" if product.proteins else "N/A",
            f"{product.carbohydrates:.1f}" if product.carbohydrates else "N/A",
            f"{product.fat:.1f}" if product.fat else "N/A",
            f"{product.fiber:.1f}" if product.fiber else "N/A",
            f"{product.salt:.1f}" if product.salt else "N/A",
        ],
        f"Pour {quantity}g (Portion)": [
            f"{energy_port:.1f}" if energy_port is not None else "N/A",
            f"{prot_port:.1f}" if prot_port is not None else "N/A",
            f"{carbs_port:.1f}" if carbs_port is not None else "N/A",
            f"{fat_port:.1f}" if fat_port is not None else "N/A",
            f"{fiber_port:.1f}" if fiber_port is not None else "N/A",
            f"{salt_port:.1f}" if salt_port is not None else "N/A",
        ],
        "% AJR (Portion)": [
            calculate_pct(energy_port, rdi['kcal']),
            calculate_pct(prot_port, rdi['proteins']),
            calculate_pct(carbs_port, rdi['carbs']),
            calculate_pct(fat_port, rdi['fat']),
            calculate_pct(fiber_port, rdi['fiber']),
            calculate_pct(salt_port, rdi['salt']),
        ]
    }

    df = pd.DataFrame(data)
    st.dataframe(df.set_index("Composant"), use_container_width=True)

    if not st.session_state.user_age and not st.session_state.user_sex:
        st.caption(
            f"Les % AJR sont calculés sur la base d'un profil par défaut ({rdi['kcal']} kcal). Renseignez votre profil dans la barre latérale pour plus de précision.")

    if product.ingredients:
        with st.expander("🔬 Ingrédients"):
            st.text(product.ingredients)

    if product.allergens:
        with st.expander("⚠️ Allergènes"):
            st.warning(", ".join([a.replace('en:', '') for a in product.allergens]))

    st.divider()

    # Le bouton utilise bien la variable 'quantity' (définie à la ligne 404)
    if st.button(f"➕ Ajouter {quantity}g de {product.name} au journal"):
        try:
            # Et 'quantity' est passée ici pour l'enregistrement
            tracker.add_consumption(product, quantity)
            st.success(f"✅ {product.name} ({quantity}g) ajouté à votre journal !")
            st.balloons()
        except Exception as e:
            st.error(f"Erreur lors de l'ajout : {e}")


# --- INTERFACE STREAMLIT PRINCIPALE ---

st.set_page_config(page_title="Analyse Nutritionnelle", page_icon="🥗", layout="wide")

# Initialiser st.session_state
if 'current_product' not in st.session_state:
    st.session_state.current_product = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'user_age' not in st.session_state:
    st.session_state.user_age = None
if 'user_sex' not in st.session_state:
    st.session_state.user_sex = None

# --- BARRE LATÉRALE (Navigation) ---
with st.sidebar:
    st.title("🥗 Analyse Nutritionnelle")

    page = st.radio(
        "Navigation",
        ["🔍 Rechercher un produit",
         "📅 Rapport Journalier",  # Renommé
         "📜 Historique",
         "ℹ️ À propos des Scores"],
        key="navigation"
    )

    st.divider()

    # --- Profil utilisateur (optionnel) ---
    st.subheader("Profil (Optionnel)")
    st.caption("Pour comparer vos apports aux recommandations (AJR)")

    sex_options = [None, "Homme", "Femme"]
    st.session_state.user_sex = st.selectbox(
        "Sexe",
        options=sex_options,
        index=sex_options.index(st.session_state.user_sex) if st.session_state.user_sex else 0,
        format_func=lambda x: x if x else "Non renseigné"
    )

    age_value = st.session_state.user_age if st.session_state.user_age else 0
    age_input = st.number_input(
        "Âge",
        min_value=0,
        max_value=120,
        value=age_value,
        step=1
    )
    st.session_state.user_age = age_input if age_input > 0 else None

    st.divider()

    with st.expander("Test Connexion"):
        with st.spinner("Vérification..."):
            try:
                requests.get("https://world.openfoodfacts.net", timeout=5)
                st.success("Connecté à OpenFoodFacts")
            except requests.exceptions.RequestException:
                st.error("Connexion échouée")

# --- PAGE 1: RECHERCHER UN PRODUIT ---
if page == "🔍 Rechercher un produit":
    st.title("🔍 Rechercher un produit")

    tab1, tab2 = st.tabs(["Par Code-barre", "Par Nom"])

    # --- Onglet 1: Recherche par Code-barre ---
    with tab1:
        with st.form("barcode_form"):
            barcode = st.text_input("📱 Entrez le code-barre du produit")
            submitted_barcode = st.form_submit_button("Rechercher")

            # Ce bloc n'est exécuté QUE au clic
            if submitted_barcode and barcode:
                with st.spinner(f"Recherche du produit {barcode}..."):
                    product_dict = api.get_product(barcode)

                if product_dict:
                    product = Product(**product_dict)
                    st.session_state.current_product = product
                else:
                    st.session_state.current_product = None
                st.session_state.search_results = []

    # --- Onglet 2: Recherche par Nom ---
    with tab2:
        with st.form("name_form"):
            query = st.text_input("🔎 Entrez le nom du produit ou la marque")
            submitted_name = st.form_submit_button("Rechercher")

            # Ce bloc n'est exécuté QUE au clic
            if submitted_name and query:
                with st.spinner(f"Recherche de '{query}'..."):
                    results = api.search_products(query, page_size=15)
                st.session_state.search_results = results
                st.session_state.current_product = None
                if not results:
                    st.warning("Aucun produit trouvé pour cette recherche.")

        # --- Affichage de la liste des résultats ---
        if st.session_state.search_results:
            st.subheader(f"Résultats pour '{query}'")
            st.caption("Cliquez sur 'Voir les détails' pour les informations nutritionnelles complètes et à jour.")

            cols = st.columns(2)
            col_index = 0

            for i, prod in enumerate(st.session_state.search_results):
                name = prod.get('product_name', 'N/A')
                brands = prod.get('brands', 'N/A')
                barcode = prod.get('code')

                with cols[col_index]:
                    with st.container(border=True):
                        st.markdown(f"**{name}**")
                        st.caption(f"Marque: {brands}")

                        if st.button("Voir les détails", key=f"details_{barcode}_{i}"):
                            with st.spinner(f"Chargement de {name}..."):
                                product_dict = api.get_product(barcode)

                                if product_dict:
                                    product = Product(**product_dict)
                                    st.session_state.current_product = product
                                else:
                                    st.session_state.current_product = None

                                st.session_state.search_results = []
                                st.rerun()

                col_index = 1 - col_index

    st.divider()

    # --- Zone d'affichage du produit sélectionné
    if st.session_state.current_product:
        display_product_details(st.session_state.current_product)


# --- PAGE 2: RAPPORT JOURNALIER (MODIFIÉE) ---
elif page == "📅 Rapport Journalier":
    st.title("📅 Rapport Journalier")  # Renommé

    selected_date = st.date_input("Choisir une date", date.today())
    date_str = selected_date.strftime("%Y-%m-%d")

    summary = tracker.get_daily_summary(date_str)

    st.header(f"Résumé du {selected_date.strftime('%d/%m/%Y')}")
    st.metric("🔢 Nombre de produits consommés", f"{summary['num_products']}")

    if summary["num_products"] == 0:
        st.info("Aucune consommation enregistrée pour cette date.")
    else:
        st.divider()
        # --- Comparaison AJR (identique) ---
        age = st.session_state.user_age
        sex = st.session_state.user_sex
        rdi = get_rdi(age, sex)
        if age or sex:
            st.subheader(f"Comparaison avec vos AJR (estimés à {rdi['kcal']} kcal)")
        else:
            st.subheader(f"Comparaison avec les AJR par défaut ({rdi['kcal']} kcal)")


        def get_percent(consumed, recommended):
            if recommended > 0: return consumed / recommended
            return 0.0


        kcal_percent = get_percent(summary['total_kcal'], rdi['kcal'])
        st.progress(min(kcal_percent, 1.0), text=f"⚡ **Énergie :** {summary['total_kcal']} / {rdi['kcal']} kcal")
        if kcal_percent > 1.0:
            st.warning(f"Dépassement de {(kcal_percent - 1.0) * 100 :.0f}% des AJR en calories.")

        cols_report = st.columns(3)
        prot_percent = get_percent(summary['total_proteins'], rdi['proteins'])
        cols_report[0].progress(min(prot_percent, 1.0),
                                text=f"💪 **Protéines :** {summary['total_proteins']} / {rdi['proteins']} g")
        carbs_percent = get_percent(summary['total_carbs'], rdi['carbs'])
        cols_report[1].progress(min(carbs_percent, 1.0),
                                text=f"🍚 **Glucides :** {summary['total_carbs']} / {rdi['carbs']} g")
        fat_percent = get_percent(summary['total_fat'], rdi['fat'])
        cols_report[2].progress(min(fat_percent, 1.0), text=f"🥑 **Lipides :** {summary['total_fat']} / {rdi['fat']} g")

        st.divider()

        # --- NOUVEAU : Tableau détaillé ---
        st.subheader("Détail des consommations du jour")
        daily_entries = tracker.get_daily_entries(date_str)

        if daily_entries:
            data_list = []
            for entry in daily_entries:
                data_list.append({
                    "Produit": entry['product_name'],
                    "Quantité (g)": entry['quantity'],
                    "Calories (kcal)": f"{entry['consumed_kcal']:.0f}" if entry['consumed_kcal'] else "N/A",
                    "Heure": datetime.fromisoformat(entry['timestamp']).strftime('%H:%M'),
                    "ID": entry['id']
                })
            df_daily = pd.DataFrame(data_list)
            st.dataframe(df_daily, use_container_width=True, hide_index=True)

    # --- NOUVEAU : Bouton Reset ---
    with st.expander("⚠️ Zone de suppression"):
        st.warning(
            f"Attention : cette action supprimera les {summary['num_products']} entrées du {date_str} de façon irréversible.")
        if st.button(f"❌ Remettre à zéro le rapport du {date_str}", disabled=(summary['num_products'] == 0)):
            tracker.delete_daily_summary(date_str)
            st.success(f"Journal du {date_str} supprimé.")
            time.sleep(1)  # Laisser le temps de lire le message
            st.rerun()


# --- PAGE 3: HISTORIQUE (MODIFIÉE) ---
elif page == "📜 Historique":
    st.title("📜 Historique des Consommations")

    days = st.number_input("Afficher les N derniers jours", min_value=1, max_value=90, value=7)

    history = tracker.get_history(days)

    if not history:
        st.info(f"Aucune consommation enregistrée sur les {days} derniers jours.")
    else:
        st.subheader(f"Affichage des {len(history)} dernières consommations")

        for entry in history:
            timestamp = datetime.fromisoformat(entry['timestamp'])

            with st.expander(f"**{timestamp.strftime('%d/%m/%Y %H:%M')}** - {entry['product_name']}"):
                st.write(f"**Produit :** {entry['product_name']}")
                st.write(f"**Quantité :** {entry['quantity']} {entry['unit']}")

                if entry['energy_kcal']:
                    consumed_kcal = (entry['energy_kcal'] * entry['quantity']) / 100
                    st.write(f"**Énergie (calculée) :** {consumed_kcal:.0f} kcal")

                st.caption(
                    f"ID Entrée: {entry['id']} | Code-barre : {entry['barcode']} | Nutri-Score : {entry['nutriscore'] or 'N/A'}")

                # --- NOUVEAU : Bouton Supprimer ---
                if st.button("Supprimer cette entrée", key=f"del_{entry['id']}", type="primary"):
                    tracker.delete_consumption_entry(entry['id'])
                    st.success(f"Entrée {entry['id']} ({entry['product_name']}) supprimée.")
                    time.sleep(1)  # Laisser le temps de lire le message
                    st.rerun()

# --- PAGE 4: À PROPOS DES SCORES ---
elif page == "ℹ️ À propos des Scores":
    st.title("ℹ️ Comprendre les Scores")
    st.caption("Cette application utilise trois indicateurs clés pour vous aider à mieux choisir vos aliments.")
    st.divider()

    # --- Nutri-Score ---
    st.subheader("📊 Nutri-Score")
    st.markdown("""
    Le **Nutri-Score** est un logo nutritionnel basé sur une échelle de 5 couleurs et lettres (de A-Vert à E-Rouge). 
    Son objectif est de fournir une information simple et compréhensible sur la **qualité nutritionnelle globale** d'un produit.

    * **Comment est-il calculé ?** Il est calculé pour 100g ou 100ml. Il pénalise les "mauvais" nutriments (calories, sucres, sel, graisses saturées) et valorise les "bons" (fibres, protéines, fruits, légumes).
    * **À quoi sert-il ?** Il permet de **comparer rapidement** des produits d'un même rayon (par exemple, deux marques de céréales). Un produit "A" est nutritionnellement meilleur qu'un produit "C".
    """)
    st.divider()

    # --- Groupe NOVA ---
    st.subheader("🏭 Groupe NOVA")
    st.markdown("""
    La classification **NOVA** n'évalue pas la qualité nutritionnelle, mais le **degré de transformation** des aliments. Elle classe les produits en 4 groupes :

    * **Groupe 1 : Aliments non ou peu transformés**
        * *Exemples :* Fruits, légumes, œufs, viande fraîche, lait pasteurisé.

    * **Groupe 2 : Ingrédients culinaires**
        * *Exemples :* Huile, beurre, sucre, sel.

    * **Groupe 3 : Aliments transformés**
        * Combinaison simple d'aliments des groupes 1 et 2.
        * *Exemples :* Fromages simples, pain frais, conserves de légumes.

    * **Groupe 4 : Aliments ultra-transformés (AUT)**
        * Formulations industrielles complexes avec de nombreux ingrédients, y compris des additifs (colorants, arômes, texturants).
        * *Exemples :* Sodas, biscuits industriels, plats préparés, céréales sucrées.
    """)
    st.divider()

    # --- Eco-Score ---
    st.subheader("🌍 Eco-Score")
    st.markdown("""
    L'**Eco-Score** est un indicateur qui évalue l'**impact environnemental** des produits alimentaires. 
    Comme le Nutri-Score, il utilise une échelle de A (très faible impact) à E (impact très fort).

    * **Comment est-il calculé ?** Il se base principalement sur l'**Analyse de Cycle de Vie (ACV)** du produit (production, transport, emballage).
    * Il utilise la base de données française **Agribalyse** (de l'ADEME).
    * Un système de **bonus/malus** est appliqué pour prendre en compte des critères comme les labels (Bio, etc.), la recyclabilité de l'emballage et l'impact sur la biodiversité.
""")