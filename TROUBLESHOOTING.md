# 🔧 Guide de Dépannage - Loto AI Predictor

Ce guide vous aidera à résoudre les problèmes courants que vous pourriez rencontrer.

## Table des Matières

1. [Problèmes d'Installation](#problèmes-dinstallation)
2. [Erreurs au Démarrage](#erreurs-au-démarrage)
3. [Problèmes de Prédiction](#problèmes-de-prédiction)
4. [Problèmes de Performance](#problèmes-de-performance)
5. [Problèmes de Scraping](#problèmes-de-scraping)
6. [Erreurs du Modèle](#erreurs-du-modèle)
7. [FAQ](#faq)

---

## Problèmes d'Installation

### ❌ `pip: command not found`

**Cause :** pip n'est pas installé ou pas dans le PATH

**Solution :**
```bash
# Sur Ubuntu/Debian
sudo apt-get install python3-pip

# Sur macOS
python3 -m ensurepip --upgrade

# Sur Windows
python -m ensurepip --upgrade
```

---

### ❌ `ModuleNotFoundError: No module named 'tensorflow'`

**Cause :** TensorFlow n'est pas installé correctement

**Solution :**
```bash
# Désinstaller et réinstaller
pip uninstall tensorflow
pip install tensorflow==2.15.0

# Si problème persiste, essayer avec CPU uniquement
pip install tensorflow-cpu==2.15.0
```

---

### ❌ Erreur lors de l'installation de TensorFlow sur Apple Silicon (M1/M2)

**Cause :** Problème de compatibilité avec ARM

**Solution :**
```bash
# Utiliser tensorflow-macos
pip install tensorflow-macos==2.15.0
pip install tensorflow-metal  # Pour accélération GPU
```

---

### ❌ `ERROR: Could not build wheels for numpy`

**Cause :** Compilateur C manquant

**Solution :**
```bash
# Sur Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# Sur macOS
xcode-select --install

# Sur Windows
# Installer Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

---

## Erreurs au Démarrage

### ❌ `Address already in use: Port 5000`

**Cause :** Le port 5000 est déjà utilisé par une autre application

**Solution 1 : Trouver et arrêter le processus**
```bash
# Sur macOS/Linux
lsof -ti:5000 | xargs kill -9

# Sur Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution 2 : Changer le port dans app.py**
```python
# Dans app.py, ligne finale
app.run(debug=True, host='0.0.0.0', port=8080)  # Utiliser port 8080
```

Puis accédez à `http://localhost:8080`

---

### ❌ `ModuleNotFoundError: No module named 'flask'`

**Cause :** Les dépendances ne sont pas installées

**Solution :**
```bash
# Réinstaller toutes les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep -i flask
```

---

### ❌ `FileNotFoundError: [Errno 2] No such file or directory: 'static'`

**Cause :** Le dossier static n'existe pas

**Solution :**
```bash
# Créer le dossier et vérifier la structure
mkdir -p static
ls -la

# Vérifier que index.html est dans static/
ls static/index.html
```

---

## Problèmes de Prédiction

### ❌ Erreur "Cannot scrape data" ou "Timeout"

**Cause :** Problème de connexion au site source

**Solution :**

1. **Vérifier votre connexion Internet**
```bash
ping loto.akroweb.fr
```

2. **Augmenter le timeout dans app.py**
```python
# Dans la fonction scrap_loto_numbers()
page = requests.get(loto_url, timeout=30)  # Au lieu de 10
```

3. **Vérifier si le site est accessible**
- Ouvrez http://loto.akroweb.fr/loto-historique-tirages/ dans votre navigateur
- Si le site est down, attendez qu'il revienne en ligne

4. **Utiliser un proxy si nécessaire**
```python
proxies = {
    'http': 'http://your-proxy:port',
    'https': 'https://your-proxy:port'
}
page = requests.get(loto_url, proxies=proxies, timeout=10)
```

---

### ❌ "Prediction returned invalid numbers"

**Cause :** Le modèle prédit des valeurs hors plage

**Solution :**

Le post-processing devrait gérer cela, mais si le problème persiste :

```python
# Dans app.py, après la prédiction
predictions = np.clip(predictions, 1, 49)  # Forcer dans [1, 49]
predictions = sorted(list(set(predictions)))  # Unicité + tri

# Si moins de 5 numéros
while len(predictions) < 5:
    new_num = np.random.randint(1, 50)
    if new_num not in predictions:
        predictions.append(new_num)
```

---

### ❌ Le bouton "Générer" ne fait rien

**Cause :** Problème JavaScript ou CORS

**Solution :**

1. **Vérifier la console du navigateur** (F12)
   - Chercher des erreurs JavaScript
   - Chercher des erreurs CORS

2. **Si erreur CORS :**
```python
# Dans app.py
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

3. **Vérifier que le serveur Flask est démarré**
```bash
curl http://localhost:5000/api/history
# Devrait retourner du JSON
```

---

## Problèmes de Performance

### 🐌 Les prédictions sont très lentes (>30 secondes)

**Cause :** Plusieurs facteurs possibles

**Solution :**

1. **Première prédiction toujours plus lente** (normal)
   - Le modèle doit être chargé ou entraîné
   - Les données doivent être scrapées

2. **Réduire le nombre d'époques pour un entraînement plus rapide**
```python
# Dans app.py
EPOCH = 500  # Au lieu de 1000
```

3. **Utiliser un modèle déjà entraîné**
   - Le modèle est sauvegardé dans `best_model.keras`
   - Les prédictions suivantes réutilisent ce modèle

4. **Optimiser le scraping**
```python
# Réduire le délai
time.sleep(1)  # Au lieu de 2
```

---

### 🐌 L'interface est lente/saccadée

**Cause :** Trop d'animations ou de particules

**Solution :**

```javascript
// Dans index.html, réduire le nombre de particules
function createParticles() {
    for (let i = 0; i < 10; i++) {  // Au lieu de 20
        // ...
    }
}
```

---

## Problèmes de Scraping

### ❌ `AttributeError: 'NoneType' object has no attribute 'find_all'`

**Cause :** Le HTML du site a changé ou la page ne charge pas

**Solution :**

1. **Vérifier manuellement le site**
```bash
curl http://loto.akroweb.fr/loto-historique-tirages/
```

2. **Mettre à jour le parser si nécessaire**
```python
# Dans scrap_loto_numbers()
# Ajouter des vérifications
if body is None:
    print("Erreur: Table non trouvée")
    return None

if not tirage_line:
    print("Erreur: Aucune ligne trouvée")
    return None
```

3. **Utiliser un User-Agent**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
page = requests.get(loto_url, headers=headers, timeout=10)
```

---

### ❌ Données manquantes ou incomplètes

**Cause :** Le site ne retourne pas toutes les données

**Solution :**

```python
# Dans scrap_loto_numbers(), ajouter des logs
for value in tirage_line:
    res = value.text.split('\n')
    print(f"Longueur de res: {len(res)}")  # Debug
    
    if len(res) < 11:
        print(f"Ligne ignorée: {res}")  # Voir pourquoi
        continue
```

---

## Erreurs du Modèle

### ❌ `ValueError: Input 0 of layer "sequential" is incompatible`

**Cause :** Shape incompatible entre données et modèle

**Solution :**

```python
# Vérifier les shapes
print(f"Train shape: {train.shape}")  # Devrait être (N, 12, 22)
print(f"Label shape: {label.shape}")  # Devrait être (N, 6)

# Si problème de features, vérifier le preprocessing
print(f"DataFrame shape: {df.shape}")  # Devrait avoir 28 colonnes (22 features + 6 originales)
```

---

### ❌ `ResourceExhaustedError: OOM when allocating tensor`

**Cause :** Mémoire insuffisante (GPU ou RAM)

**Solution :**

1. **Réduire le batch size**
```python
BATCHSIZE = 16  # Au lieu de 30
```

2. **Réduire le nombre d'unités LSTM**
```python
UNITS = 64  # Au lieu de 100
```

3. **Utiliser le CPU au lieu du GPU**
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
```

---

### ❌ Le modèle ne s'entraîne pas (loss ne diminue pas)

**Cause :** Problème de données ou d'hyperparamètres

**Solution :**

1. **Vérifier les données**
```python
# Ajouter des prints
print(f"Min/Max values: {df.min()}, {df.max()}")
print(f"NaN count: {df.isna().sum()}")
```

2. **Essayer un learning rate différent**
```python
from tensorflow.keras.optimizers import Adam
optimizer = Adam(learning_rate=0.001)
model.compile(loss=LOSS, optimizer=optimizer)
```

3. **Augmenter la patience**
```python
EarlyStopping(monitor='val_loss', mode='min', patience=400)
```

---

## FAQ

### Q: Combien de temps pour la première prédiction ?

**R:** 10-30 secondes. Le système doit scraper ~1000 tirages, extraire 22 features, entraîner ou charger le modèle LSTM, puis prédire.

---

### Q: Pourquoi les prédictions changent à chaque fois ?

**R:** Le modèle LSTM analyse les patterns historiques qui évoluent. De plus, il y a de la randomisation dans l'entraînement et le post-processing.

---

### Q: Le système peut-il vraiment prédire les numéros gagnants ?

**R:** **NON.** Les tirages de loterie sont totalement aléatoires. Ce système analyse des patterns statistiques mais ne peut PAS prédire le futur. Utilisez-le uniquement à des fins éducatives.

---

### Q: Comment améliorer la précision du modèle ?

**R:** Quelques suggestions (mais ça ne garantit pas plus de gains) :
- Augmenter le nombre de features
- Essayer d'autres architectures (GRU, Transformer)
- Augmenter le window_length
- Ajouter des données externes (météo, événements, etc.)

**Mais rappel :** Même avec un modèle parfait, la loterie reste du hasard pur.

---

### Q: Puis-je déployer en production ?

**R:** Techniquement oui, mais :
1. Ajoutez un reverse proxy (nginx)
2. Utilisez Gunicorn/uWSGI
3. Ajoutez du rate limiting
4. Sécurisez avec HTTPS
5. **Incluez toujours les avertissements légaux**

---

### Q: Le modèle est-il sauvegardé ?

**R:** Oui, dans `best_model.keras`. Il est réutilisé automatiquement aux prochaines prédictions.

---

### Q: Comment réentraîner le modèle ?

**R:** 
```bash
# Option 1: Supprimer le fichier
rm best_model.keras

# Option 2: Dans la requête API
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"retrain": true}'
```

---

### Q: L'application fonctionne-t-elle hors ligne ?

**R:** Non, elle a besoin d'Internet pour :
- Scraper les données historiques
- Charger les fonts Google
- Charger Tailwind CSS et Chart.js (CDN)

Pour un fonctionnement hors ligne, téléchargez ces ressources localement.

---

### Q: Puis-je utiliser ce système pour d'autres loteries ?

**R:** Oui, mais vous devrez :
1. Modifier la fonction `scrap_loto_numbers()` pour votre source
2. Ajuster les plages de numéros dans la config
3. Adapter le feature engineering si nécessaire

---

## Support Supplémentaire

Si votre problème n'est pas listé ici :

1. **Vérifiez les logs** : Regardez la console Flask pour les erreurs détaillées
2. **Mode debug** : Activez le debug dans app.py pour plus d'infos
3. **Ouvrez une issue** : Décrivez votre problème avec logs et captures d'écran

---

**Rappel :** Ce système est à but éducatif. Les prédictions ne garantissent aucun gain. Jouez de manière responsable ! 🎲
