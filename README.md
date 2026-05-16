# ◼ QR Studio

> Générateur de QR codes personnalisés avec aperçu en temps réel, construit avec Streamlit et Python.

---

## Aperçu

QR Studio est une application web locale qui permet de créer des QR codes entièrement personnalisables : couleurs, formes, dégradés, logo intégré, et sept types de contenu différents. L'aperçu se met à jour automatiquement à chaque modification d'un paramètre, sans avoir à cliquer sur un bouton.

---

## Fonctionnalités

- **Aperçu live** — le QR code se régénère instantanément à chaque changement
- **7 types de contenu** — URL, texte libre, e-mail, téléphone, SMS, Wi-Fi, vCard
- **6 formes de modules** — carré, carré espacé, cercle, arrondi, barres verticales/horizontales
- **5 types de dégradés** — uni, radial, carré, horizontal, vertical
- **Logo centré** — importez votre propre image avec fond arrondi automatique
- **Niveau de correction d'erreur** configurable (L / M / Q / H)
- **Export** en PNG et JPEG

---

## Installation

### Prérequis

- Python 3.10 ou supérieur
- `pip`

### Étapes

```bash
# 1. Cloner ou télécharger le projet
git clone https://github.com/votre-utilisateur/qr-studio.git
cd qr-studio

# 2. (Optionnel) Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run qr_generator.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

---

## Dépendances

| Package | Rôle |
|---|---|
| `streamlit >= 1.35` | Interface web et gestion de l'état |
| `qrcode[pil] >= 7.4` | Génération et stylisation des QR codes |
| `Pillow >= 10.0` | Traitement d'image et composition du logo |

Toutes les dépendances sont listées dans `requirements.txt`.

---

## Structure du projet

```
qr-studio/
├── qr_generator.py   # Application principale
├── requirements.txt  # Dépendances Python
└── README.md         # Ce fichier
```

---

## Guide d'utilisation

### Onglet Contenu

Sélectionnez le type de contenu puis remplissez les champs correspondants. Le QR code se met à jour dès la première saisie.

| Type | Format encodé |
|---|---|
| URL | `https://…` |
| Email | `mailto:adresse?subject=…&body=…` |
| Téléphone | `tel:+33…` |
| SMS | `sms:+33…?body=…` |
| Wi-Fi | `WIFI:T:WPA;S:nom;P:mdp;;` |
| vCard | Standard vCard 3.0 |

Le **niveau de correction d'erreur** détermine la quantité de données de redondance :
- `L` (7 %) — QR code le plus dense, moins robuste
- `H` (30 %) — recommandé lorsqu'un logo est ajouté

### Onglet Style

- **Forme des modules** — change l'apparence de chaque cellule du QR code
- **Couleur QR / Fond** — deux color pickers indépendants
- **Dégradé** — combine la couleur principale avec une couleur secondaire selon différentes géométries
- **Taille & marge** — ajuste la résolution de l'image exportée et l'espace blanc autour du code

### Onglet Logo

Importez une image (PNG, JPG, WEBP). Elle sera automatiquement centrée avec un fond blanc arrondi pour garantir la lisibilité. Ajustez sa taille entre 10 % et 35 % de la largeur du QR code.

> **Conseil** : utilisez toujours le niveau de correction `H` lorsqu'un logo est présent, car il masque une partie des modules.

---

## Comment fonctionne l'aperçu dynamique

Streamlit relance le script complet à chaque interaction avec un widget. QR Studio exploite ce comportement en calculant une **empreinte** (tuple) de tous les paramètres courants. À chaque re-run :

1. Si l'empreinte a changé → le QR est régénéré et mis en cache dans `st.session_state`
2. Si l'empreinte est identique → l'image mise en cache est réaffichée sans recalcul

Ce mécanisme évite les régénérations inutiles tout en garantissant un aperçu toujours à jour.

---

## Licence

Projet open-source, libre d'utilisation et de modification.
