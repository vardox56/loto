#!/bin/bash

# Script de démarrage rapide pour Loto AI Predictor
# Ce script installe les dépendances et lance l'application

echo "================================================"
echo "🔮 LOTO AI PREDICTOR - Installation & Démarrage"
echo "================================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé sur ce système"
    echo "Veuillez installer Python 3.8 ou supérieur depuis https://www.python.org"
    exit 1
fi

echo "✅ Python détecté : $(python3 --version)"
echo ""

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip n'est pas installé"
    echo "Installation de pip..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip détecté"
echo ""

# Créer un environnement virtuel (optionnel mais recommandé)
read -p "Voulez-vous créer un environnement virtuel ? (recommandé) [o/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[OoYy]$ ]]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    
    # Activer l'environnement virtuel
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    echo "✅ Environnement virtuel activé"
    echo ""
fi

# Installer les dépendances
echo "📥 Installation des dépendances Python..."
echo "⚠️  Cela peut prendre plusieurs minutes (TensorFlow est volumineux)..."
echo ""

pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Toutes les dépendances sont installées avec succès !"
    echo ""
else
    echo ""
    echo "❌ Erreur lors de l'installation des dépendances"
    echo "Veuillez vérifier les messages d'erreur ci-dessus"
    exit 1
fi

# Demander si l'utilisateur veut lancer l'application maintenant
read -p "Voulez-vous lancer l'application maintenant ? [O/n] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "Pour lancer l'application plus tard, exécutez :"
    echo "  python3 app.py"
    echo ""
    echo "Puis ouvrez votre navigateur sur : http://localhost:5000"
    exit 0
fi

# Lancer l'application
echo ""
echo "🚀 Lancement de l'application..."
echo "================================================"
echo ""
echo "📍 Serveur démarré sur : http://localhost:5000"
echo "🌐 Ouvrez cette URL dans votre navigateur"
echo ""
echo "⚠️  Avertissement : Ce système est à but éducatif uniquement"
echo "   Les prédictions ne garantissent aucun gain à la loterie"
echo ""
echo "Pour arrêter le serveur, appuyez sur Ctrl+C"
echo ""
echo "================================================"
echo ""

python3 app.py
