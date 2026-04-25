"""
Script de test rapide pour vérifier que le scraper fonctionne
"""

from web_scraper_advanced import AdvancedWebScraper

print("🧪 Test du Web Scraper Avancé")
print("-" * 50)

try:
    # Créer le scraper
    scraper = AdvancedWebScraper()
    print("✓ Scraper initialisé")

    # Tester sur une page simple
    print("\n🌐 Scraping de https://example.com (page de test)...")

    content = scraper.scrape(
        url="https://example.com",
        download_images=False,  # Pas d'images pour le test
        export_formats=['md']   # Seulement Markdown
    )

    print("\n✅ TEST RÉUSSI!")
    print(f"   • Titre: {content['title']}")
    print(f"   • Texte extrait: {len(content['text'])} caractères")
    print(f"   • Fichier MD créé dans: scraped_content/")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    print("\nVérifiez que vous avez:")
    print("  1. Installé les dépendances: pip install -r requirements_scraper.txt")
    print("  2. Google Chrome installé sur votre système")
