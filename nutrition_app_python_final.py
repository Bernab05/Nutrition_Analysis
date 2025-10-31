"""
Application d'Analyse Nutritionnelle - OpenFoodFacts
Version Finale avec toutes les corrections

INSTALLATION:
pip install requests

UTILISATION:
python nutrition_app.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path
import time


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


class OpenFoodFactsAPI:
    """Client API OpenFoodFacts avec gestion robuste"""
    
    BASE_URL = "https://world.openfoodfacts.net/api/v2"
    SEARCH_URL = "https://world.openfoodfacts.net"
    USER_AGENT = "NutritionAnalyzer/1.0 (Educational Project)"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        
        # Configuration de retry automatique
        try:
            from requests.adapters import HTTPAdapter
            from requests.packages.urllib3.util.retry import Retry
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        except:
            pass
    
    def get_product(self, barcode: str) -> Optional[Product]:
        """Récupère les données d'un produit via son code-barre"""
        url = f"{self.BASE_URL}/product/{barcode}"
        params = {
            "fields": "product_name,brands,nutrition_grades,nova_group,"
                     "ecoscore_grade,nutriments,ingredients_text,allergens_tags"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != 1:
                print(f"❌ Produit {barcode} non trouvé dans la base OpenFoodFacts")
                return None
            
            return self._parse_product(barcode, data["product"])
            
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout - Le serveur met trop de temps à répondre")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API: {e}")
            return None
    
    def _parse_product(self, barcode: str, data: Dict) -> Product:
        """Parse la réponse API vers objet Product"""
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
    
    def search_products(self, query: str, page_size: int = 20) -> List[Dict]:
        """Recherche produits par mots-clés"""
        url = f"{self.SEARCH_URL}/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": min(page_size, 100)
        }
        
        try:
            print(f"   Interrogation du serveur (timeout 30s)...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])
            
            if products:
                return products
            
            print(f"   Aucun résultat, essai méthode alternative...")
            return self._search_alternative(query, page_size)
            
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout - Essai avec méthode alternative...")
            return self._search_alternative(query, page_size)
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return self._search_alternative(query, page_size)
    
    def _search_alternative(self, query: str, page_size: int = 20) -> List[Dict]:
        """Méthode alternative de recherche"""
        try:
            if query.isdigit() and len(query) >= 8:
                url = f"{self.BASE_URL}/search"
                params = {
                    "code": query,
                    "page_size": 1,
                    "fields": "code,product_name,brands,nutrition_grades"
                }
            else:
                url = f"{self.BASE_URL}/search"
                params = {
                    "page_size": min(page_size, 50),
                    "fields": "code,product_name,brands,nutrition_grades",
                    "brands_tags": query.lower().replace(" ", "-")
                }
            
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
        except:
            return []


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
        print(f"\n✅ Consommation enregistrée: {product.name} ({quantity}{unit})")
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """Calcule le résumé nutritionnel d'une journée"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
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
        """, (date,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "date": date,
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
        
        cursor.execute("""
            SELECT * FROM consumption
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """, (days,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results


class NutritionAnalyzer:
    """Analyseur nutritionnel principal"""
    
    def __init__(self):
        self.api = OpenFoodFactsAPI()
        self.tracker = ConsumptionTracker()
    
    def analyze_product(self, barcode: str) -> Optional[Product]:
        """Analyse un produit et affiche ses informations"""
        print(f"\n🔍 Recherche du produit {barcode}...")
        product = self.api.get_product(barcode)
        
        if not product:
            return None
        
        print(f"\n{'='*60}")
        print(f"📦 {product.name}")
        print(f"🏷️  Marque: {product.brands or 'Non renseigné'}")
        print(f"{'='*60}")
        
        print(f"\n📊 SCORES")
        print(f"  • Nutri-Score: {product.nutriscore or 'Non calculé'}")
        print(f"  • Groupe NOVA: {product.nova_group or 'Non disponible'}")
        print(f"  • Eco-Score: {product.ecoscore or 'Non calculé'}")
        
        print(f"\n🍽️  POUR 100g")
        print(f"  • Énergie: {product.energy_kcal or 'N/A'} kcal")
        print(f"  • Protéines: {product.proteins or 'N/A'} g")
        print(f"  • Glucides: {product.carbohydrates or 'N/A'} g")
        print(f"  • Lipides: {product.fat or 'N/A'} g")
        print(f"  • Fibres: {product.fiber or 'N/A'} g")
        print(f"  • Sel: {product.salt or 'N/A'} g")
        
        if product.allergens:
            print(f"\n⚠️  ALLERGÈNES")
            for allergen in product.allergens:
                print(f"  • {allergen.replace('en:', '')}")
        
        return product
    
    def show_daily_report(self):
        """Affiche le rapport journalier"""
        summary = self.tracker.get_daily_summary()
        
        print(f"\n{'='*60}")
        print(f"📅 RAPPORT DU {summary['date']}")
        print(f"{'='*60}")
        print(f"🔢 Nombre de produits: {summary['num_products']}")
        print(f"⚡ Énergie totale: {summary['total_kcal']} kcal")
        print(f"💪 Protéines: {summary['total_proteins']} g")
        print(f"🍚 Glucides: {summary['total_carbs']} g")
        print(f"🥑 Lipides: {summary['total_fat']} g")
        print(f"{'='*60}\n")
    
    def show_history(self, days: int = 7):
        """Affiche l'historique des consommations"""
        history = self.tracker.get_history(days)
        
        if not history:
            print(f"\n📭 Aucune consommation enregistrée sur les {days} derniers jours")
            return
        
        print(f"\n{'='*60}")
        print(f"📜 HISTORIQUE ({days} derniers jours)")
        print(f"{'='*60}")
        
        for entry in history[:20]:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            print(f"\n🕐 {timestamp.strftime('%d/%m/%Y %H:%M')}")
            print(f"   {entry['product_name']}")
            print(f"   Quantité: {entry['quantity']}{entry['unit']}")
            if entry['energy_kcal']:
                consumed_kcal = (entry['energy_kcal'] * entry['quantity']) / 100
                print(f"   Énergie: {consumed_kcal:.0f} kcal")


class InteractiveMenu:
    """Interface en ligne de commande interactive"""
    
    def __init__(self):
        self.analyzer = NutritionAnalyzer()
        self.running = True
        self._test_connectivity()
    
    def _test_connectivity(self):
        """Teste la connectivité au serveur OpenFoodFacts"""
        print("\n" + "="*60)
        print("🔌 TEST DE CONNEXION À OPENFOODFACTS")
        print("="*60)
        print("\n⏳ Vérification de la connexion au serveur...")
        
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
                if elapsed > 5:
                    print("⚠️  Le serveur est un peu lent")
            else:
                print(f"⚠️  Réponse anormale (code {response.status_code})")
                
        except requests.exceptions.Timeout:
            print("⚠️  TIMEOUT - Le serveur est très lent")
        except requests.exceptions.ConnectionError:
            print("❌ ERREUR DE CONNEXION")
            print("   Vérifiez votre connexion internet")
        except Exception as e:
            print(f"❌ ERREUR: {type(e).__name__}: {str(e)}")
        
        print("\n" + "="*60)
        try:
            input("\n📥 Appuyez sur Entrée pour continuer...")
        except Exception:
            time.sleep(2)
        print("\n")
    
    def show_menu(self):
        """Affiche le menu principal"""
        print("\n" + "="*60)
        print("🥗 APPLICATION D'ANALYSE NUTRITIONNELLE")
        print("="*60)
        print("\n📋 MENU PRINCIPAL")
        print("\n[1] ou [B] Rechercher par CODE-BARRE")
        print("[2] ou [N] Rechercher par NOM")
        print("[3] ou [A] Ajouter au journal")
        print("[4] ou [R] Voir le rapport du jour")
        print("[5] ou [H] Voir l'historique")
        print("[0] ou [Q] Quitter")
        print("\n💡 Utilisez les chiffres du clavier principal")
        print("   ou les lettres indiquées")
        print("\n" + "="*60)
    
    def search_by_barcode(self):
        """Recherche par code-barre"""
        print("\n" + "-"*60)
        try:
            barcode = input("📱 Entrez le code-barre (ou 'q' pour annuler): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            return
        
        if barcode.lower() == 'q':
            return
        
        if not barcode:
            print("❌ Code-barre invalide")
            return
        
        self.analyzer.analyze_product(barcode)
        
        try:
            input("\n📥 Appuyez sur Entrée pour continuer...")
        except:
            time.sleep(1)
    
    def search_by_name(self):
        """Recherche par nom de produit"""
        print("\n" + "-"*60)
        
        try:
            query = input("🔎 Entrez le nom du produit (ou 'q' pour annuler): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            return
        
        if query.lower() == 'q':
            return
        
        if not query:
            print("❌ Recherche invalide")
            return
        
        print(f"\n🔍 Recherche de '{query}'...")
        print("⏳ Patience, cela peut prendre jusqu'à 30 secondes...")
        
        results = self.analyzer.api.search_products(query, page_size=10)
        
        if not results:
            print("\n❌ Aucun produit trouvé")
            print("\n💡 SUGGESTIONS:")
            print("   • Essayez un terme plus simple")
            print("   • Vérifiez l'orthographe")
            print("   • Utilisez le code-barre (option 1) si vous l'avez")
            try:
                input("\n📥 Appuyez sur Entrée pour continuer...")
            except:
                time.sleep(1)
            return
        
        print(f"\n✅ {len(results)} produits trouvés:\n")
        print(f"{'#':<4} {'Nom':<35} {'Marque':<20} {'Score':<12}")
        print("-"*75)
        
        for i, product in enumerate(results, 1):
            name = product.get('product_name', 'N/A')[:34]
            brand = product.get('brands', 'N/A')[:19]
            score = product.get('nutrition_grades', 'N/A').upper()
            print(f"{i:<4} {name:<35} {brand:<20} {score:<12}")
        
        print("\n" + "-"*60)
        
        try:
            choice = input("\n📱 Numéro pour détails (ou Entrée pour annuler): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            return
        
        try:
            if choice and choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(results):
                    selected = results[choice_num - 1]
                    barcode = selected.get('code')
                    if barcode:
                        self.analyzer.analyze_product(barcode)
                else:
                    print(f"\n❌ Numéro invalide (1-{len(results)})")
            elif choice:
                print("\n❌ Entrez un numéro valide")
        except ValueError:
            print("\n❌ Entrée invalide")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
        
        try:
            input("\n📥 Appuyez sur Entrée pour continuer...")
        except (EOFError, KeyboardInterrupt):
            pass
        except Exception:
            time.sleep(1)
    
    def add_to_diary(self):
        """Ajoute un produit au journal"""
        print("\n" + "-"*60)
        
        try:
            barcode = input("📱 Code-barre du produit (ou 'q'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            return
        
        if barcode.lower() == 'q':
            return
        
        if not barcode:
            print("❌ Code-barre invalide")
            try:
                input("\n📥 Appuyez sur Entrée...")
            except:
                time.sleep(1)
            return
        
        product = self.analyzer.api.get_product(barcode)
        if not product:
            try:
                input("\n📥 Appuyez sur Entrée...")
            except:
                time.sleep(1)
            return
        
        print(f"\n✅ Produit: {product.name}")
        
        try:
            quantity_input = input("\n📏 Quantité en grammes (défaut 100g): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            return
        
        try:
            quantity = float(quantity_input) if quantity_input else 100.0
            self.analyzer.tracker.add_consumption(product, quantity)
        except ValueError:
            print("❌ Quantité invalide, utilisation de 100g")
            self.analyzer.tracker.add_consumption(product, 100.0)
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        try:
            input("\n📥 Appuyez sur Entrée pour continuer...")
        except (EOFError, KeyboardInterrupt):
            pass
        except Exception:
            time.sleep(1)
    
    def show_daily_report(self):
        """Affiche le rapport du jour"""
        try:
            self.analyzer.show_daily_report()
        except Exception as e:
            print(f"\n❌ Erreur lors de l'affichage du rapport: {e}")
        
        try:
            input("\n📥 Appuyez sur Entrée pour continuer...")
        except (EOFError, KeyboardInterrupt):
            pass
        except Exception:
            time.sleep(1)
    
    def show_history(self):
        """Affiche l'historique"""
        print("\n" + "-"*60)
        
        try:
            days_input = input("📅 Nombre de jours (défaut 7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            return
        
        try:
            days = int(days_input) if days_input else 7
        except ValueError:
            days = 7
            print(f"⚠️  Valeur invalide, utilisation de {days} jours")
        
        try:
            self.analyzer.show_history(days)
        except Exception as e:
            print(f"\n❌ Erreur lors de l'affichage: {e}")
        
        try:
            input("\n📥 Appuyez sur Entrée pour continuer...")
        except (EOFError, KeyboardInterrupt):
            pass
        except Exception:
            time.sleep(1)
    
    def run(self):
        """Lance l'application interactive"""
        print("\n" + "="*60)
        print("🎉 BIENVENUE DANS L'ANALYSEUR NUTRITIONNEL!")
        print("="*60)
        print("📊 Alimenté par OpenFoodFacts (2.9M+ produits)")
        print("🍎 Suivez votre alimentation en temps réel")
        print("="*60)
        
        while self.running:
            try:
                self.show_menu()
                
                try:
                    choice = input("\n👉 Votre choix: ").strip().upper()
                except EOFError:
                    print("\n❌ Erreur de lecture. Réessayez...")
                    continue
                except KeyboardInterrupt:
                    raise
                
                choice_map = {
                    '1': '1', 'B': '1',
                    '2': '2', 'N': '2',
                    '3': '3', 'A': '3',
                    '4': '4', 'R': '4',
                    '5': '5', 'H': '5',
                    '0': '0', 'Q': '0', 'QUIT': '0', 'EXIT': '0'
                }
                
                choice = choice_map.get(choice, choice)
                
                if choice == '1':
                    self.search_by_barcode()
                elif choice == '2':
                    self.search_by_name()
                elif choice == '3':
                    self.add_to_diary()
                elif choice == '4':
                    self.show_daily_report()
                elif choice == '5':
                    self.show_history()
                elif choice == '0':
                    print("\n" + "="*60)
                    print("👋 AU REVOIR ET BON APPÉTIT!")
                    print("="*60)
                    self.running = False
                else:
                    print(f"\n❌ Choix '{choice}' invalide")
                    print("💡 Utilisez 1-5 ou B,N,A,R,H,Q")
                    try:
                        input("\n📥 Appuyez sur Entrée...")
                    except:
                        time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n" + "="*60)
                print("👋 INTERRUPTION - AU REVOIR!")
                print("="*60)
                self.running = False
            except Exception as e:
                print(f"\n❌ Erreur inattendue: {type(e).__name__}")
                print(f"   Détails: {str(e)}")
                print("   L'application continue...")
                try:
                    input("\n📥 Appuyez sur Entrée...")
                except:
                    time.sleep(1)


if __name__ == "__main__":
    app = InteractiveMenu()
    app.run()
