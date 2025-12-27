# Tests API pour Loto AI Predictor

Ce fichier contient des exemples de requêtes API que vous pouvez utiliser pour tester le système.

## Prérequis

Assurez-vous que le serveur Flask est démarré :
```bash
python app.py
```

## Tests avec curl

### 1. Générer une prédiction

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"retrain": false}'
```

**Réponse attendue :**
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

### 2. Récupérer l'historique

```bash
curl http://localhost:5000/api/history
```

**Réponse attendue :**
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

### 3. Obtenir les statistiques

```bash
curl http://localhost:5000/api/stats
```

**Réponse attendue :**
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

## Tests avec Python

### Script de test complet

```python
import requests
import json

API_URL = "http://localhost:5000/api"

def test_prediction():
    """Test de génération de prédiction"""
    print("🔮 Test : Génération de prédiction")
    
    response = requests.post(
        f"{API_URL}/predict",
        json={"retrain": False}
    )
    
    data = response.json()
    
    if data['success']:
        print("✅ Succès !")
        print(f"Numéros prédits : {data['predictions']}")
        print(f"Numéro chance : {data['chance']}")
        print(f"Statistiques : {data['stats']}")
    else:
        print(f"❌ Erreur : {data.get('error')}")
    
    print()

def test_history():
    """Test de récupération de l'historique"""
    print("📜 Test : Récupération de l'historique")
    
    response = requests.get(f"{API_URL}/history")
    data = response.json()
    
    if data['success']:
        print(f"✅ Succès ! {len(data['history'])} tirages récupérés")
        print(f"Dernier tirage : {data['history'][0]}")
    else:
        print(f"❌ Erreur : {data.get('error')}")
    
    print()

def test_stats():
    """Test de récupération des statistiques"""
    print("📊 Test : Récupération des statistiques")
    
    response = requests.get(f"{API_URL}/stats")
    data = response.json()
    
    if data['success']:
        print("✅ Succès !")
        print(f"Total de tirages : {data['stats']['total_tirages']}")
        print(f"Top 3 numéros : {data['stats']['top_numbers'][:3]}")
    else:
        print(f"❌ Erreur : {data.get('error')}")
    
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("Tests API - Loto AI Predictor")
    print("=" * 50)
    print()
    
    try:
        test_prediction()
        test_history()
        test_stats()
        
        print("=" * 50)
        print("✅ Tous les tests sont terminés !")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        print("Assurez-vous que le serveur Flask est démarré sur le port 5000")
```

## Tests avec Postman

### Configuration

1. Créez une nouvelle collection "Loto AI Predictor"
2. Ajoutez les requêtes suivantes :

#### Requête 1 : Prédiction
- **Méthode :** POST
- **URL :** `http://localhost:5000/api/predict`
- **Headers :**
  - Content-Type: application/json
- **Body (raw JSON) :**
```json
{
  "retrain": false
}
```

#### Requête 2 : Historique
- **Méthode :** GET
- **URL :** `http://localhost:5000/api/history`

#### Requête 3 : Statistiques
- **Méthode :** GET
- **URL :** `http://localhost:5000/api/stats`

## Tests avec JavaScript (fetch)

```javascript
// Test de prédiction
async function testPrediction() {
    try {
        const response = await fetch('http://localhost:5000/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ retrain: false })
        });
        
        const data = await response.json();
        console.log('Prédiction:', data);
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Test d'historique
async function testHistory() {
    try {
        const response = await fetch('http://localhost:5000/api/history');
        const data = await response.json();
        console.log('Historique:', data);
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Test de statistiques
async function testStats() {
    try {
        const response = await fetch('http://localhost:5000/api/stats');
        const data = await response.json();
        console.log('Statistiques:', data);
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Lancer tous les tests
testPrediction();
testHistory();
testStats();
```

## Codes de statut HTTP

- **200 OK** : Requête réussie
- **400 Bad Request** : Données invalides
- **500 Internal Server Error** : Erreur serveur (scraping échoué, modèle non chargé, etc.)

## Notes importantes

1. La première prédiction peut prendre plus de temps (téléchargement des données + chargement du modèle)
2. Le scraping peut échouer si le site source est indisponible
3. Le modèle LSTM prend environ 5-10 secondes pour générer une prédiction
4. Les prédictions sont basées sur l'analyse statistique et ne garantissent aucun gain

## Dépannage

### Erreur de connexion
- Vérifiez que le serveur Flask est démarré
- Vérifiez que le port 5000 n'est pas bloqué par un firewall

### Erreur 500
- Consultez les logs du serveur Flask
- Vérifiez que toutes les dépendances sont installées
- Vérifiez la connexion Internet (pour le scraping)

### Timeout
- Augmentez le timeout dans la configuration
- Vérifiez votre connexion Internet
