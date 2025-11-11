"""
Exemples d'utilisation du Web Scraper Avancé
============================================

Ce fichier contient différents exemples d'utilisation du scraper
pour différents cas d'usage.
"""

from web_scraper_advanced import AdvancedWebScraper, ScraperConfig


# ==================== EXEMPLE 1 : Usage Simple ====================

def exemple_1_basique():
    """
    Exemple le plus simple : scraper avec les paramètres par défaut
    """
    print("📝 EXEMPLE 1 : Scraping basique")
    print("-" * 50)

    scraper = AdvancedWebScraper()

    content = scraper.scrape(
        url="https://example.com",
        download_images=True,
        export_formats=['md', 'docx']
    )

    print(f"✓ Titre: {content['title']}")
    print(f"✓ Texte extrait: {len(content['text'])} caractères")


# ==================== EXEMPLE 2 : Configuration Personnalisée ====================

def exemple_2_config_custom():
    """
    Utiliser une configuration personnalisée
    """
    print("\n📝 EXEMPLE 2 : Configuration personnalisée")
    print("-" * 50)

    # Créer une config custom
    config = ScraperConfig()

    # Personnaliser
    config.HEADLESS = False  # Voir le navigateur en action
    config.PAGE_LOAD_TIMEOUT = 60  # Timeout plus long
    config.SCROLL_TO_BOTTOM = True  # Activer le scroll
    config.OUTPUT_DIR = "mes_resultats"  # Dossier personnalisé

    scraper = AdvancedWebScraper(config)

    content = scraper.scrape(
        url="https://example.com/blog/article",
        download_images=False,  # Ne pas télécharger les images
        export_formats=['md']  # Seulement Markdown
    )

    print(f"✓ Export dans: {config.OUTPUT_DIR}/")


# ==================== EXEMPLE 3 : Scraper Plusieurs Pages ====================

def exemple_3_multiple_urls():
    """
    Scraper plusieurs URLs en boucle
    """
    print("\n📝 EXEMPLE 3 : Scraping multiple URLs")
    print("-" * 50)

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]

    scraper = AdvancedWebScraper()

    resultats = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Scraping: {url}")
        try:
            content = scraper.scrape(
                url=url,
                download_images=False,  # Performance
                export_formats=['md']
            )
            resultats.append(content)
            print(f"  ✓ Réussi")
        except Exception as e:
            print(f"  ✗ Erreur: {e}")
            continue

    print(f"\n✓ {len(resultats)}/{len(urls)} pages scrapées avec succès")


# ==================== EXEMPLE 4 : Extraction Ciblée ====================

def exemple_4_extraction_ciblee():
    """
    Scraper et extraire seulement certains éléments
    """
    print("\n📝 EXEMPLE 4 : Extraction ciblée")
    print("-" * 50)

    scraper = AdvancedWebScraper()

    content = scraper.scrape(
        url="https://example.com/data-table",
        download_images=False,
        export_formats=['md']
    )

    # Extraire seulement les tableaux
    print(f"\n📊 Tableaux trouvés: {len(content['tables'])}")
    for i, table in enumerate(content['tables'], 1):
        print(f"\nTableau {i}: {table['title']}")
        print(f"  - {len(table['rows'])} lignes")
        print(f"  - {len(table['rows'][0]) if table['rows'] else 0} colonnes")

    # Extraire seulement les liens
    print(f"\n🔗 Liens trouvés: {len(content['links'])}")
    for link in content['links'][:5]:  # Afficher les 5 premiers
        print(f"  - {link['text']}: {link['url']}")


# ==================== EXEMPLE 5 : Gestion d'Erreurs ====================

def exemple_5_gestion_erreurs():
    """
    Gérer les erreurs de scraping de manière robuste
    """
    print("\n📝 EXEMPLE 5 : Gestion d'erreurs")
    print("-" * 50)

    urls = [
        "https://site-valide.com",
        "https://site-inexistant-12345.com",  # Va échouer
        "https://site-qui-bloque.com",  # Peut échouer
    ]

    scraper = AdvancedWebScraper()

    succes = 0
    echecs = 0

    for url in urls:
        try:
            content = scraper.scrape(
                url=url,
                download_images=False,
                export_formats=['md']
            )
            print(f"✓ {url} - OK")
            succes += 1

        except Exception as e:
            print(f"✗ {url} - ERREUR: {str(e)[:50]}...")
            echecs += 1
            # Continuer malgré l'erreur
            continue

    print(f"\nRésumé: {succes} succès, {echecs} échecs")


# ==================== EXEMPLE 6 : Mode Performance ====================

def exemple_6_performance():
    """
    Configuration optimisée pour la performance
    """
    print("\n📝 EXEMPLE 6 : Mode performance")
    print("-" * 50)

    config = ScraperConfig()

    # Optimisations
    config.HEADLESS = True  # Pas d'interface (+ rapide)
    config.DISABLE_IMAGES = True  # Ne pas charger les images (+ rapide)
    config.SCROLL_TO_BOTTOM = False  # Pas de scroll (+ rapide)
    config.PAGE_LOAD_TIMEOUT = 15  # Timeout court

    scraper = AdvancedWebScraper(config)

    import time
    start = time.time()

    content = scraper.scrape(
        url="https://example.com",
        download_images=False,  # Ne pas télécharger
        export_formats=['md']  # Seulement un format
    )

    duration = time.time() - start
    print(f"✓ Scraping terminé en {duration:.2f} secondes")


# ==================== EXEMPLE 7 : Extraction de Métadonnées ====================

def exemple_7_metadata():
    """
    Se concentrer sur l'extraction de métadonnées
    """
    print("\n📝 EXEMPLE 7 : Extraction de métadonnées")
    print("-" * 50)

    scraper = AdvancedWebScraper()

    content = scraper.scrape(
        url="https://example.com/article",
        download_images=False,
        export_formats=['md']
    )

    # Afficher les métadonnées
    print("\n📋 Métadonnées de la page:")
    print(f"  • Titre: {content['title']}")

    if content.get('metadata'):
        for key, value in content['metadata'].items():
            print(f"  • {key}: {value[:100]}{'...' if len(value) > 100 else ''}")


# ==================== EXEMPLE 8 : Export Personnalisé ====================

def exemple_8_export_custom():
    """
    Traiter le contenu avant l'export
    """
    print("\n📝 EXEMPLE 8 : Traitement personnalisé")
    print("-" * 50)

    scraper = AdvancedWebScraper()

    content = scraper.scrape(
        url="https://example.com",
        download_images=True,
        export_formats=[]  # Pas d'export automatique
    )

    # Traiter le contenu
    text = content['text']

    # Exemple: extraire seulement les 1000 premiers caractères
    text_court = text[:1000] + "..."

    # Créer un export personnalisé
    with open('mon_export_custom.txt', 'w', encoding='utf-8') as f:
        f.write(f"Titre: {content['title']}\n\n")
        f.write(f"URL: {content['url']}\n\n")
        f.write(f"Résumé:\n{text_court}\n\n")
        f.write(f"Nombre de tableaux: {len(content['tables'])}\n")
        f.write(f"Nombre d'images: {len(content['images'])}\n")

    print("✓ Export personnalisé créé: mon_export_custom.txt")


# ==================== EXEMPLE 9 : Analyse de Structure ====================

def exemple_9_analyse_structure():
    """
    Analyser la structure du contenu d'une page
    """
    print("\n📝 EXEMPLE 9 : Analyse de structure")
    print("-" * 50)

    scraper = AdvancedWebScraper()

    content = scraper.scrape(
        url="https://example.com",
        download_images=False,
        export_formats=[]
    )

    # Statistiques
    print("\n📊 Statistiques du contenu:")
    print(f"  • Longueur du texte: {len(content['text'])} caractères")
    print(f"  • Nombre de mots: {len(content['text'].split())}")
    print(f"  • Nombre de lignes: {len(content['text'].split(chr(10)))}")
    print(f"  • Nombre de tableaux: {len(content.get('tables', []))}")
    print(f"  • Nombre d'images: {len(content.get('images', []))}")
    print(f"  • Nombre de liens: {len(content.get('links', []))}")

    # Analyser les tableaux
    if content.get('tables'):
        print("\n  📊 Détails des tableaux:")
        for i, table in enumerate(content['tables'], 1):
            rows = table['rows']
            cols = len(rows[0]) if rows else 0
            print(f"    • Tableau {i}: {len(rows)} lignes × {cols} colonnes")


# ==================== EXEMPLE 10 : Mode Debug ====================

def exemple_10_debug():
    """
    Activer le mode debug pour voir ce qui se passe
    """
    print("\n📝 EXEMPLE 10 : Mode debug")
    print("-" * 50)

    config = ScraperConfig()
    config.HEADLESS = False  # Voir le navigateur

    scraper = AdvancedWebScraper(config)

    # Le scraper va afficher beaucoup d'informations dans la console
    # et dans scraper.log

    content = scraper.scrape(
        url="https://example.com",
        download_images=True,
        export_formats=['md', 'docx']
    )

    print("\n✓ Consultez scraper.log pour voir tous les détails")


# ==================== MAIN ====================

def main():
    """
    Exécuter tous les exemples (commentez ceux que vous ne voulez pas)
    """
    print("=" * 70)
    print("         EXEMPLES D'UTILISATION - WEB SCRAPER AVANCÉ")
    print("=" * 70)

    # Décommenter les exemples que vous voulez tester

    # exemple_1_basique()
    # exemple_2_config_custom()
    # exemple_3_multiple_urls()
    # exemple_4_extraction_ciblee()
    # exemple_5_gestion_erreurs()
    # exemple_6_performance()
    # exemple_7_metadata()
    # exemple_8_export_custom()
    # exemple_9_analyse_structure()
    # exemple_10_debug()

    print("\n" + "=" * 70)
    print("ℹ️  Décommentez les exemples dans main() pour les exécuter")
    print("=" * 70)


if __name__ == "__main__":
    main()
