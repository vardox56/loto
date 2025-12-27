# 🔮 Loto AI Predictor

Système de prédiction de numéros de loterie utilisant un réseau de neurones LSTM (Long Short-Term Memory) pour analyser les patterns historiques.

## ⚠️ Avertissement Important

**CE SYSTÈME EST À BUT ÉDUCATIF ET DE RECHERCHE UNIQUEMENT.**

- Les tirages de loterie sont **totalement aléatoires**
- Les prédictions basées sur l'historique n'augmentent **pas** vos chances de gagner
- La probabilité de gagner reste de **1 sur 1 906 884** (pour 5 numéros corrects)
- **Jouez de manière responsable** - Les jeux d'argent comportent des risques

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Navigateur web moderne

### Étape 1 : Cloner ou télécharger les fichiers

Assurez-vous d'avoir tous les fichiers suivants :
```
loto-ai-predictor/
│
├── app.py                    # Backend Flask
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
└── static/
    └── index.html           # Frontend web
```

### Étape 2 : Installer les dépendances

Ouvrez un terminal dans le dossier du projet et exécutez :

```bash
pip install -r requirements.txt
```

**Note :** L'installation de TensorFlow peut prendre plusieurs minutes.

### Étape 3 : Lancer l'application

```bash
python app.py
```

Vous devriez voir :
```
 * Running on http://0.0.0.0:5000
```

### Étape 4 : Accéder à l'interface

Ouvrez votre navigateur et allez à :
```
http://localhost:5000
```

## 📖 Utilisation

### Génération de Prédictions

1. Cliquez sur **"🔮 Générer une Prédiction"**
2. Le système va :
   - Récupérer les données historiques en temps réel
   - Appliquer le feature engineering (20+ caractéristiques)
   - Exécuter le modèle LSTM
   - Afficher les numéros prédits

3. Les résultats incluent :
   - **5 numéros** entre 1 et 49
   - **1 numéro chance** entre 1 et 10
   - **Statistiques** : pairs/impairs, bas/haut, somme, moyenne

### Historique des Tirages

Cliquez sur **"📜 Charger l'Historique"** pour voir les 20 derniers tirages officiels du Loto français.

## 🤖 Architecture Technique

### Modèle d'IA

- **Type :** LSTM (Long Short-Term Memory) Neural Network
- **Framework :** TensorFlow/Keras
- **Architecture :**
  - Couche LSTM (100 unités) avec return_sequences=True
  - Couche LSTM (100 unités) avec dropout 0.1
  - Couche Dense (6 sorties)
  - Optimiseur : Adam
  - Loss : MAE (Mean Absolute Error)

### Feature Engineering

Le système extrait **22 caractéristiques** de chaque tirage :

**Caractéristiques de base :**
- Les 5 numéros du tirage
- Le numéro chance

**Caractéristiques calculées :**
- Fréquence de chaque numéro
- Nombre de pairs/impairs
- Nombre de numéros bas (≤24) / hauts (>24)
- Somme des différences au carré
- Moyenne, médiane, écart-type
- Plage (max - min)
- Somme totale
- Ratio impairs/pairs

### Pipeline de Traitement

1. **Scraping** : Récupération des données depuis http://loto.akroweb.fr
2. **Prétraitement** : Feature engineering + nettoyage
3. **Normalisation** : StandardScaler sur toutes les features
4. **Sliding Window** : Fenêtre glissante de 12 tirages
5. **Prédiction** : Modèle LSTM prédit les 6 prochains numéros
6. **Post-traitement** : Dénormalisation + ajustement dans les plages valides

## 🔧 Configuration

### Paramètres du Modèle (dans app.py)

```python
UNITS = 100              # Nombre d'unités LSTM
BATCHSIZE = 30          # Taille des batchs
EPOCH = 1000            # Nombre d'époques max
OPTIMIZER = 'adam'      # Optimiseur
LOSS = 'mae'            # Fonction de perte
DROPOUT = 0.1           # Taux de dropout
window_length = 12      # Longueur de la fenêtre temporelle
```

### Entraînement du Modèle

Le modèle s'entraîne automatiquement la première fois, puis est sauvegardé dans `best_model.keras`.

Pour forcer un réentraînement, modifiez dans l'interface ou l'API :
```javascript
fetch(`${API_URL}/predict`, {
    method: 'POST',
    body: JSON.stringify({ retrain: true })
})
```

## 🌐 API Endpoints

### POST /api/predict

Génère une nouvelle prédiction.

**Body :**
```json
{
  "retrain": false
}
```

**Response :**
```json
{
  "success": true,
  "predictions": [3, 12, 25, 38, 47],
  "chance": 7,
  "stats": {
    "pairs": 3,
    "impairs": 2,
    "bas": 2,
    "haut": 3,
    "somme": 125,
    "moyenne": 25.0
  },
  "timestamp": "2024-12-26T10:30:00",
  "model_status": "loaded"
}
```

### GET /api/history

Récupère les 20 derniers tirages réels.

**Response :**
```json
{
  "success": true,
  "history": [
    {
      "date": "23 Décembre 2024",
      "numbers": [5, 18, 22, 35, 44],
      "chance": 9
    }
  ]
}
```

### GET /api/stats

Récupère les statistiques globales.

**Response :**
```json
{
  "success": true,
  "stats": {
    "total_tirages": 1234,
    "top_numbers": [
      {"number": 13, "frequency": 156},
      {"number": 7, "frequency": 142}
    ],
    "pairs_avg": 2.5,
    "impairs_avg": 2.5
  }
}
```

## 📊 Statistiques de Performance

Le modèle LSTM analyse :
- **1000+ tirages historiques**
- **22 caractéristiques** par tirage
- **Fenêtre temporelle** de 12 tirages
- **Early stopping** avec patience de 200 époques

## 🐛 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier que toutes les dépendances sont installées
pip install -r requirements.txt

# Vérifier que le port 5000 est disponible
# Sur Windows : netstat -ano | findstr :5000
# Sur Mac/Linux : lsof -i :5000
```

### Erreur "Cannot scrape data"

Le site source peut être temporairement indisponible. Réessayez plus tard.

### Erreur TensorFlow

```bash
# Réinstaller TensorFlow
pip uninstall tensorflow
pip install tensorflow==2.15.0
```

### L'interface ne se charge pas

Assurez-vous que :
1. Le serveur Flask est bien démarré
2. Vous accédez à `http://localhost:5000` (pas file://)
3. Le dossier `static/` contient bien `index.html`

## 🔬 Développement

### Structure du Code

```
app.py
├── Fonctions de scraping
│   └── scrap_loto_numbers()
├── Fonctions de feature engineering
│   ├── freq_val()
│   ├── is_pair(), is_impair()
│   ├── calculate_mean(), calculate_std()
│   └── ...
├── Fonctions de modélisation
│   ├── define_model()
│   ├── create_lstm_dataset()
│   └── preprocess_data()
└── Routes API
    ├── /api/predict
    ├── /api/history
    └── /api/stats
```

### Ajouter de Nouvelles Features

1. Créer une fonction dans `app.py` :
```python
def my_new_feature(data):
    return data['num0'] * 2  # Exemple
```

2. L'ajouter dans `preprocess_data()` :
```python
df['my_feature'] = my_new_feature(df)
```

3. Le modèle utilisera automatiquement cette nouvelle feature

## 📝 Licence

MIT License - Libre d'utilisation à des fins éducatives et de recherche.

## 🤝 Contribution

Ce projet est à but éducatif. Les contributions pour améliorer le modèle ou l'interface sont bienvenues.

## 📧 Support

Pour toute question ou problème, consultez la documentation ou ouvrez une issue.

---

**Rappel Final :** Ce système analyse des patterns historiques mais ne peut PAS prédire des événements aléatoires. Utilisez-le uniquement à des fins éducatives pour comprendre le machine learning et les réseaux de neurones. Ne jouez jamais plus que ce que vous pouvez vous permettre de perdre.

**© 2024 - Loto AI Predictor - Système d'analyse par Intelligence Artificielle**
"# loto" 
