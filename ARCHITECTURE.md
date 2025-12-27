# 🏗️ Architecture du Système Loto AI Predictor

## Vue d'Ensemble

Le système Loto AI Predictor est composé de trois couches principales qui communiquent ensemble pour fournir des prédictions basées sur l'apprentissage profond.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Web)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Interface Utilisateur (HTML/CSS/JavaScript)             │  │
│  │  - Design moderne et interactif                          │  │
│  │  - Affichage des prédictions                             │  │
│  │  - Visualisation des statistiques                        │  │
│  │  - Historique des tirages                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask API)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Routes API                                              │  │
│  │  - POST /api/predict  → Génération de prédictions       │  │
│  │  - GET  /api/history  → Récupération de l'historique    │  │
│  │  - GET  /api/stats    → Calcul des statistiques         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Preprocessing Pipeline                                  │  │
│  │  - Web scraping des données                              │  │
│  │  - Feature engineering (22 features)                     │  │
│  │  - Normalisation (StandardScaler)                        │  │
│  │  - Création de séquences temporelles                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Modèle LSTM (TensorFlow/Keras)                         │  │
│  │  - Architecture LSTM bidirectionnelle                    │  │
│  │  - Prédiction sur fenêtre glissante                      │  │
│  │  - Sauvegarde et chargement du modèle                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sources de données                                      │  │
│  │  - Web scraping (loto.akroweb.fr)                        │  │
│  │  - Modèle sauvegardé (best_model.keras)                  │  │
│  │  - Configuration (config.json)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Détaillée

### 1. Frontend Layer

#### Technologies
- **HTML5** : Structure sémantique
- **CSS3** : Design moderne avec animations
- **JavaScript (Vanilla)** : Logique client sans framework

#### Composants Principaux
```
static/index.html
├── Header
│   ├── Titre animé
│   └── Sous-titre avec badges
├── Warning Banner
│   └── Avertissement légal
├── Control Panel (Sidebar)
│   ├── Boutons d'action
│   ├── Info technique
│   └── Status badge
├── Prediction Zone
│   ├── Display des numéros
│   ├── Statistiques de prédiction
│   └── Loading states
└── History Section
    └── Liste des tirages récents
```

#### Design System
```css
:root {
  --primary: #0a0e27;      /* Fond principal */
  --secondary: #1a1f3a;    /* Fond secondaire */
  --accent: #00ff88;       /* Couleur d'accent */
  --danger: #ff0055;       /* Alertes */
  --text: #e8e8e8;         /* Texte principal */
  --border: rgba(...);     /* Bordures */
}
```

**Typographie :**
- Display : `Playfair Display` (900) - Titres élégants
- Corps : `JetBrains Mono` - Code-like appearance

**Animations :**
- `@keyframes popIn` : Apparition des boules
- `@keyframes float` : Particules flottantes
- `@keyframes pulse` : Badge de statut
- Transitions fluides (0.3s ease)

---

### 2. Backend Layer (Flask)

#### Structure du Code
```python
app.py
├── Configuration
│   ├── Paramètres du modèle (UNITS, EPOCHS, etc.)
│   ├── Constantes (pairs, impairs)
│   └── Chemins de fichiers
│
├── Scraping Module
│   └── scrap_loto_numbers()
│       ├── BeautifulSoup parser
│       ├── Extraction des données HTML
│       └── Conversion en DataFrame
│
├── Feature Engineering
│   ├── freq_val() - Fréquence des numéros
│   ├── is_pair() / is_impair() - Détection pairs/impairs
│   ├── is_under() - Classification basse/haute
│   ├── sum_diff() - Différences consécutives
│   ├── calculate_mean() - Statistiques basiques
│   ├── calculate_median()
│   ├── calculate_std()
│   ├── calculate_range()
│   ├── sum_numbers()
│   └── odd_even_ratio()
│
├── Data Preprocessing
│   ├── preprocess_data()
│   │   ├── Feature extraction
│   │   ├── Nettoyage (NaN, Inf)
│   │   └── Ordonnancement chronologique
│   └── create_lstm_dataset()
│       ├── StandardScaler normalization
│       ├── Sliding window creation
│       └── Train/Label split
│
├── Model Definition
│   └── define_model()
│       ├── Sequential architecture
│       ├── LSTM layers (2x)
│       ├── Dense output layer
│       └── Compilation (adam, mae)
│
└── API Routes
    ├── POST /api/predict
    │   ├── Scrape data
    │   ├── Preprocess
    │   ├── Load/train model
    │   ├── Generate prediction
    │   └── Return JSON
    ├── GET /api/history
    │   ├── Scrape recent draws
    │   └── Return formatted history
    └── GET /api/stats
        ├── Calculate frequencies
        ├── Top numbers analysis
        └── Global statistics
```

#### Flux de Prédiction
```
1. Requête POST /api/predict
   ↓
2. Scraping des données historiques
   ↓
3. Feature Engineering (22 features par tirage)
   ↓
4. Normalisation avec StandardScaler
   ↓
5. Création d'une fenêtre glissante (12 derniers tirages)
   ↓
6. Prédiction LSTM
   ↓
7. Dénormalisation
   ↓
8. Post-processing (validation, tri, unicité)
   ↓
9. Retour JSON avec statistiques
```

---

### 3. Machine Learning Layer

#### Architecture du Modèle LSTM

```
Input Shape: (12, 22)
    │ 12 = window_length (12 tirages)
    │ 22 = nombre de features
    │
    ↓
┌─────────────────────────────────┐
│  LSTM Layer 1                   │
│  - Units: 100                   │
│  - Return sequences: True       │
│  - Activation: tanh             │
└─────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────┐
│  LSTM Layer 2                   │
│  - Units: 100                   │
│  - Dropout: 0.1                 │
│  - Return sequences: False      │
└─────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────┐
│  Dense Layer                    │
│  - Units: 6                     │
│  - Activation: linear           │
└─────────────────────────────────┘
    │
    ↓
Output Shape: (6,)
    │ [num0, num1, num2, num3, num4, chance]
```

#### Paramètres d'Entraînement
- **Optimizer :** Adam
- **Loss Function :** MAE (Mean Absolute Error)
- **Batch Size :** 30
- **Epochs :** 1000 (max)
- **Validation Split :** 20%
- **Early Stopping :** Patience de 200 epochs

#### Features Engineering (22 features)

**Catégorie 1 : Valeurs Brutes (6)**
1. num0, num1, num2, num3, num4 (5 numéros)
2. chance (numéro chance)

**Catégorie 2 : Fréquences (6)**
3. freq_num0, freq_num1, freq_num2, freq_num3, freq_num4
4. freq_chance

**Catégorie 3 : Caractéristiques Binaires (5)**
5. pair (nombre de pairs)
6. impair (nombre d'impairs)
7. pair_chance (chance est pair)
8. impair_chance (chance est impair)
9. is_under_24 (numéros ≤ 24)
10. is_under_40 (numéros ≤ 40)

**Catégorie 4 : Statistiques Calculées (5)**
11. mean (moyenne)
12. median (médiane)
13. std (écart-type)
14. range (max - min)
15. sum (somme totale)
16. odd_even_ratio (ratio impairs/pairs)
17. sum_diff (somme des différences²)

---

### 4. Data Flow

#### Flux Complet d'une Prédiction

```
┌──────────────┐
│   Browser    │
│  (Frontend)  │
└──────┬───────┘
       │ 1. Click "Générer"
       │
       ▼
┌──────────────────────────────────────┐
│  JavaScript                          │
│  - fetch('POST /api/predict')        │
│  - Display loading animation         │
└──────┬───────────────────────────────┘
       │ 2. HTTP Request
       │
       ▼
┌──────────────────────────────────────┐
│  Flask Backend                       │
│  Route: POST /api/predict            │
└──────┬───────────────────────────────┘
       │ 3. Execute prediction pipeline
       │
       ▼
┌──────────────────────────────────────┐
│  Scraping Module                     │
│  - GET loto.akroweb.fr               │
│  - Parse HTML table                  │
│  - Extract ~1000+ draws              │
└──────┬───────────────────────────────┘
       │ 4. Raw data (DataFrame)
       │
       ▼
┌──────────────────────────────────────┐
│  Feature Engineering                 │
│  - Calculate 22 features             │
│  - Clean data (NaN, Inf)             │
│  - Reverse chronological order       │
└──────┬───────────────────────────────┘
       │ 5. Processed DataFrame
       │
       ▼
┌──────────────────────────────────────┐
│  Data Preparation                    │
│  - StandardScaler fit/transform      │
│  - Create sliding windows (12)       │
│  - Prepare sequences                 │
└──────┬───────────────────────────────┘
       │ 6. Normalized sequences
       │
       ▼
┌──────────────────────────────────────┐
│  Model Loading/Training              │
│  - Check if best_model.keras exists  │
│  - Load OR train new model           │
│  - Early stopping if training        │
└──────┬───────────────────────────────┘
       │ 7. Trained model
       │
       ▼
┌──────────────────────────────────────┐
│  LSTM Prediction                     │
│  - Take last 12 draws                │
│  - model.predict()                   │
│  - Get 6 normalized outputs          │
└──────┬───────────────────────────────┘
       │ 8. Normalized predictions
       │
       ▼
┌──────────────────────────────────────┐
│  Post-Processing                     │
│  - Inverse scaling                   │
│  - Clip to valid range (1-49, 1-10)  │
│  - Ensure uniqueness                 │
│  - Sort numbers                      │
│  - Calculate statistics              │
└──────┬───────────────────────────────┘
       │ 9. Final predictions + stats
       │
       ▼
┌──────────────────────────────────────┐
│  JSON Response                       │
│  {                                   │
│    "success": true,                  │
│    "predictions": [3, 12, 25, ...],  │
│    "chance": 7,                      │
│    "stats": {...}                    │
│  }                                   │
└──────┬───────────────────────────────┘
       │ 10. HTTP Response
       │
       ▼
┌──────────────────────────────────────┐
│  JavaScript                          │
│  - Parse JSON                        │
│  - displayPrediction()               │
│  - Animate number balls              │
│  - Show statistics                   │
└──────┬───────────────────────────────┘
       │ 11. DOM Update
       │
       ▼
┌──────────────┐
│   Browser    │
│  (Updated)   │
└──────────────┘
```

---

### 5. Sécurité et Bonnes Pratiques

#### Validation des Données
```python
# Validation côté serveur
- Vérification des types de données
- Nettoyage des valeurs infinies/NaN
- Clip des valeurs dans les plages valides
- Gestion des erreurs de scraping
```

#### Gestion des Erreurs
```python
try:
    # Logic
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

#### CORS
```python
CORS(app)  # Permet les requêtes cross-origin
```

#### Rate Limiting
- Le scraping inclut un délai (2s) pour éviter de surcharger le serveur source

---

### 6. Performance et Optimisation

#### Mise en Cache
- Le modèle entraîné est sauvegardé (best_model.keras)
- Chargement du modèle depuis le cache évite le réentraînement

#### Optimisations
- **Early Stopping** : Arrêt automatique si pas d'amélioration
- **Model Checkpoint** : Sauvegarde du meilleur modèle uniquement
- **Batch Processing** : Traitement par lots (batch_size=30)
- **Validation Split** : 20% des données pour validation

#### Temps de Réponse Typiques
- **Première prédiction** : 10-30 secondes (scraping + load)
- **Prédictions suivantes** : 5-10 secondes (modèle en cache)
- **Historique** : 2-5 secondes (scraping uniquement)
- **Statistiques** : 2-5 secondes (scraping + calculs)

---

### 7. Déploiement

#### Développement
```bash
python app.py
# Serveur sur http://localhost:5000
# Debug mode activé
```

#### Production (recommandations)
```bash
# Utiliser Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Ou avec uWSGI
uwsgi --http :5000 --wsgi-file app.py --callable app
```

#### Docker (optionnel)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

### 8. Monitoring et Logs

#### Logs Flask
```python
app.logger.info("Prediction generated")
app.logger.error(f"Error: {e}")
```

#### Métriques à Suivre
- Temps de réponse des endpoints
- Taux de succès du scraping
- Précision du modèle (MAE, loss)
- Nombre de requêtes par heure

---

## Conclusion

Cette architecture modulaire permet :
- ✅ **Séparation des responsabilités** (Frontend / Backend / ML)
- ✅ **Scalabilité** (API REST facile à étendre)
- ✅ **Maintenabilité** (Code organisé et documenté)
- ✅ **Performance** (Mise en cache du modèle)
- ✅ **Sécurité** (Validation, gestion d'erreurs)

Le système est conçu pour être **éducatif** et démontrer l'utilisation de l'apprentissage profond sur des données séquentielles, tout en rappelant constamment que les prédictions de loterie restent du domaine du hasard.
