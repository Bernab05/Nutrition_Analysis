# 🕷️ Web Scraper Avancé - Version 2.0

Scraper web professionnel avec gestion avancée des cas bloquants et export multi-formats (Markdown + Word).

---

## 📋 Fonctionnalités

### ✅ Gestion des Cas Bloquants

Le scraper intègre de nombreuses techniques pour contourner les protections courantes :

| Protection | Solution Implémentée |
|------------|---------------------|
| **Anti-bot détection** | User-Agent rotation, suppression des marqueurs automation |
| **Cloudflare / WAF** | Détection + mode stealth, headers personnalisés |
| **Rate limiting** | Retry automatique avec backoff exponentiel |
| **Timeouts** | Timeouts configurables + gestion d'erreurs robuste |
| **SSL/TLS** | Désactivation de la vérification pour les certificats invalides |
| **Pop-ups / Cookies** | Fermeture automatique des bannières courantes |
| **Lazy loading** | Scroll automatique pour charger le contenu dynamique |
| **JavaScript** | Support complet via Selenium + attente du chargement |
| **Redirections** | Gestion automatique |
| **Captcha** | Détection (nécessite intervention manuelle) |

### 📤 Export Multi-formats

- **Markdown (.md)** : Format léger et portable
- **Word (.docx)** : Format professionnel avec mise en forme

### 🎯 Extraction Complète

Le scraper extrait :
- ✅ **Texte principal** : Contenu nettoyé et structuré
- ✅ **Tableaux** : Conversion automatique en format Markdown/Word
- ✅ **Images** : Téléchargement local + intégration dans les exports
- ✅ **Liens** : Extraction de tous les hyperliens
- ✅ **Métadonnées** : Title, description, Open Graph, etc.

---

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Google Chrome installé (pour Selenium)

### Étapes

1. **Installer les dépendances** :
   ```bash
   pip install -r requirements_scraper.txt
   ```

2. **Vérifier l'installation** :
   ```bash
   python web_scraper_advanced.py
   ```

---

## 💻 Utilisation

### Mode Interactif (Recommandé)

```bash
python web_scraper_advanced.py
```

Le script vous guidera à travers les options :
1. Entrer l'URL à scraper
2. Choisir si vous voulez télécharger les images
3. Sélectionner les formats d'export (MD, Word, ou les deux)
4. Options avancées (mode headless, scroll, proxy)

### Exemple d'exécution

```
======================================================================
           WEB SCRAPER AVANCÉ - Version 2.0
======================================================================

🌐 Entrez l'URL du site à scraper: example.com/article

📋 OPTIONS:
Télécharger les images? (o/N): o
Exporter en Markdown? (O/n): o
Exporter en Word? (O/n): o

Options avancées? (o/N): n

🚀 Démarrage du scraping...

[INFO] Driver Chrome créé avec succès
[INFO] Tentative 1/3 : Chargement de https://example.com/article
[INFO] ✓ Page chargée avec succès
[INFO] Scroll vers le bas pour charger le contenu dynamique...
[INFO] Extraction du contenu...
[INFO] ✓ 3 tableau(x) extrait(s)
[INFO] ✓ 15 image(s) trouvée(s)
[INFO] ✓ 45 lien(s) extrait(s)
[INFO] Téléchargement de 15 images...
Images: 100%|████████████████| 15/15 [00:08<00:00,  1.75it/s]
[INFO] ✓ 15 image(s) téléchargée(s)
[INFO] Génération du fichier Markdown: scraped_content/example_com_20250111_143022.md
[INFO] ✓ Fichier Markdown généré
[INFO] Génération du fichier Word: scraped_content/example_com_20250111_143022.docx
[INFO] ✓ Fichier Word généré

✅ SCRAPING RÉUSSI!

📁 Résultats dans le dossier: scraped_content/
   - Texte extrait: 12450 caractères
   - Tableaux: 3
   - Images: 15
   - Liens: 45
```

---

## 🛠️ Utilisation Programmatique

Vous pouvez également utiliser le scraper dans vos propres scripts Python :

```python
from web_scraper_advanced import AdvancedWebScraper, ScraperConfig

# Configuration personnalisée
config = ScraperConfig()
config.HEADLESS = True  # Mode sans interface
config.SCROLL_TO_BOTTOM = True  # Activer le scroll
config.PAGE_LOAD_TIMEOUT = 45  # Timeout personnalisé

# Créer le scraper
scraper = AdvancedWebScraper(config)

# Scraper une URL
content = scraper.scrape(
    url="https://example.com",
    download_images=True,
    export_formats=['md', 'docx']  # ou ['md'] ou ['docx']
)

# Accéder au contenu
print(f"Titre: {content['title']}")
print(f"Texte: {content['text'][:200]}...")
print(f"Nombre d'images: {len(content['images'])}")
```

---

## ⚙️ Configuration Avancée

Le fichier `web_scraper_advanced.py` contient une classe `ScraperConfig` que vous pouvez personnaliser :

```python
class ScraperConfig:
    # Liste de User-Agents (rotation automatique)
    USER_AGENTS = [...]

    # Timeouts (secondes)
    PAGE_LOAD_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15
    SCROLL_PAUSE_TIME = 2

    # Retry
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    BACKOFF_FACTOR = 2

    # Dossiers de sortie
    OUTPUT_DIR = "scraped_content"
    IMAGES_DIR = "images"

    # Options de scraping
    HEADLESS = True  # Mode sans interface
    DISABLE_IMAGES = False  # Désactiver pour performance
    SCROLL_TO_BOTTOM = True  # Pour lazy loading

    # Éléments à supprimer du HTML
    UNWANTED_TAGS = ["script", "style", "nav", "footer", ...]
    UNWANTED_CLASSES = ["advertisement", "ad", "popup", ...]
```

---

## 📂 Structure des Fichiers de Sortie

Après l'exécution, vous trouverez :

```
scraped_content/
├── example_com_20250111_143022.md        # Export Markdown
├── example_com_20250111_143022.docx      # Export Word
└── images/                                # Images téléchargées
    ├── image_1.jpg
    ├── image_2.png
    └── ...
```

---

## 🎨 Formats d'Export

### Markdown (.md)

Structure du fichier Markdown :

```markdown
# Titre de la Page

**URL source**: https://example.com
**Date d'extraction**: 2025-01-11T14:30:22

---

## 📋 Métadonnées
- **description**: Description de la page
- **keywords**: mot1, mot2, mot3
- **author**: Auteur

---

## 📄 Contenu Textuel
[Texte principal de la page]

---

## 📊 Tableaux (2)
### Tableau 1
| Colonne 1 | Colonne 2 |
|-----------|-----------|
| Donnée 1  | Donnée 2  |

---

## 🖼️ Images (10)
### Image 1: Description
![Description](images/image_1.jpg)

---

## 🔗 Liens Extraits (45)
- [Texte du lien](https://url.com)

---

**Fin du document**
```

### Word (.docx)

Le fichier Word contient :
- Titre centré en style Heading 0
- Métadonnées formatées
- Texte avec paragraphes
- Tableaux avec style "Light Grid Accent 1"
- Images intégrées (largeur max 6 pouces)
- Liens sous forme de liste à puces

---

## 🐛 Résolution de Problèmes

### Erreur : "Chrome driver not found"

**Solution** : Le script télécharge automatiquement le driver via `webdriver-manager`. Assurez-vous que Chrome est installé.

```bash
# Ubuntu/Debian
sudo apt install chromium-browser

# macOS
brew install --cask google-chrome

# Windows
Télécharger depuis: https://www.google.com/chrome/
```

### Erreur : "Timeout lors du chargement"

**Solutions** :
1. Augmenter les timeouts dans `ScraperConfig`
2. Vérifier votre connexion internet
3. Le site peut être temporairement indisponible

```python
config.PAGE_LOAD_TIMEOUT = 60  # Augmenter à 60 secondes
```

### Détection de Cloudflare / Captcha

**Symptôme** : Le log indique "⚠️ Blocage détecté: Cloudflare"

**Solutions** :
1. Activer le mode non-headless pour voir ce qui se passe :
   ```python
   config.HEADLESS = False
   ```

2. Installer `undetected-chromedriver` (décommenter dans requirements) :
   ```bash
   pip install undetected-chromedriver
   ```

   Puis modifier le code pour l'utiliser :
   ```python
   import undetected_chromedriver as uc
   driver = uc.Chrome(options=options)
   ```

3. Utiliser un proxy / VPN si le site bloque votre IP

4. Pour les Captchas : résolution manuelle nécessaire (mode non-headless)

### Images non téléchargées

**Causes possibles** :
- Images en lazy loading : activez `SCROLL_TO_BOTTOM = True`
- URLs relatives mal formées : le script tente de les corriger automatiquement
- Images protégées : certaines images peuvent nécessiter l'authentification

### Contenu incomplet

**Solutions** :
1. Augmenter le délai de scroll :
   ```python
   config.SCROLL_PAUSE_TIME = 5  # Attendre 5 secondes entre les scrolls
   ```

2. Vérifier que JavaScript est activé :
   ```python
   config.ENABLE_JAVASCRIPT = True
   ```

3. Le site peut charger le contenu via AJAX après interaction utilisateur

---

## 📊 Logging

Tous les événements sont enregistrés dans `scraper.log` avec différents niveaux :

```
2025-01-11 14:30:22 - WebScraper - INFO - Driver Chrome créé avec succès
2025-01-11 14:30:25 - WebScraper - INFO - ✓ Page chargée avec succès
2025-01-11 14:30:26 - WebScraper - WARNING - ⚠️ Blocage détecté: Cloudflare
2025-01-11 14:30:30 - WebScraper - INFO - ✓ 15 image(s) téléchargée(s)
```

Consultez ce fichier pour déboguer les problèmes.

---

## 🔐 Considérations Légales et Éthiques

⚠️ **Important** :

1. **Respectez les conditions d'utilisation** : Vérifiez les CGU du site avant de scraper
2. **Consultez robots.txt** : `https://example.com/robots.txt`
3. **Rate limiting** : Ne surchargez pas les serveurs (le scraper implémente déjà des délais)
4. **Copyright** : Le contenu scrapé peut être protégé par copyright
5. **Usage personnel** : Utilisez ce scraper de manière responsable

---

## 🤝 Contribution

Améliorations possibles :
- [ ] Support de proxies multiples avec rotation
- [ ] Intégration d'`undetected-chromedriver` par défaut
- [ ] Support de résolution de Captcha via services tiers
- [ ] Export en PDF
- [ ] Mode batch (scraper plusieurs URLs)
- [ ] Interface graphique (GUI)
- [ ] Support de l'authentification (login)
- [ ] Scraping de sites avec pagination

---

## 📝 Notes Techniques

### Architecture

Le scraper est organisé en classes modulaires :

- **`ScraperConfig`** : Configuration centralisée
- **`AdvancedWebDriver`** : Gestion du navigateur Selenium
- **`ContentExtractor`** : Extraction et parsing du contenu
- **`ImageDownloader`** : Téléchargement des images
- **`MarkdownExporter`** : Export Markdown
- **`WordExporter`** : Export Word
- **`AdvancedWebScraper`** : Orchestrateur principal

### Dépendances Clés

- **Selenium 4.15+** : Automation du navigateur
- **BeautifulSoup 4.12+** : Parsing HTML
- **python-docx 1.1+** : Génération de documents Word
- **requests 2.31+** : Téléchargement d'images
- **tqdm 4.66+** : Progress bars

---

## 📞 Support

Pour toute question ou problème :
1. Consultez le fichier `scraper.log`
2. Vérifiez la section "Résolution de Problèmes" ci-dessus
3. Ouvrez une issue sur le dépôt GitHub (si applicable)

---

## 📜 Licence

Ce code est fourni à des fins éducatives. Utilisez-le de manière responsable et conformément aux lois applicables.

---

**Version** : 2.0
**Dernière mise à jour** : Janvier 2025
**Auteur** : Claude AI
