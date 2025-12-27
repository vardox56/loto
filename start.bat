@echo off
chcp 65001 > nul
title Loto AI Predictor - Installation et Démarrage

echo ================================================
echo 🔮 LOTO AI PREDICTOR - Installation et Démarrage
echo ================================================
echo.

REM Vérifier si Python est installé
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé sur ce système
    echo Veuillez installer Python 3.8 ou supérieur depuis https://www.python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python détecté
python --version
echo.

REM Vérifier si pip est installé
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip n'est pas installé
    echo Installation de pip...
    python -m ensurepip --upgrade
)

echo ✅ pip détecté
echo.

REM Demander si l'utilisateur veut créer un environnement virtuel
set /p create_venv="Voulez-vous créer un environnement virtuel ? (recommandé) [O/n]: "
if /i "%create_venv%"=="n" goto :install_deps

echo 📦 Création de l'environnement virtuel...
python -m venv venv

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo ✅ Environnement virtuel activé
echo.

:install_deps
REM Installer les dépendances
echo 📥 Installation des dépendances Python...
echo ⚠️  Cela peut prendre plusieurs minutes (TensorFlow est volumineux)...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors de l'installation des dépendances
    echo Veuillez vérifier les messages d'erreur ci-dessus
    pause
    exit /b 1
)

echo.
echo ✅ Toutes les dépendances sont installées avec succès !
echo.

REM Demander si l'utilisateur veut lancer l'application
set /p launch_app="Voulez-vous lancer l'application maintenant ? [O/n]: "
if /i "%launch_app%"=="n" (
    echo.
    echo Pour lancer l'application plus tard, exécutez :
    echo   python app.py
    echo.
    echo Puis ouvrez votre navigateur sur : http://localhost:5000
    echo.
    pause
    exit /b 0
)

REM Lancer l'application
echo.
echo 🚀 Lancement de l'application...
echo ================================================
echo.
echo 📍 Serveur démarré sur : http://localhost:5000
echo 🌐 Ouvrez cette URL dans votre navigateur
echo.
echo ⚠️  Avertissement : Ce système est à but éducatif uniquement
echo    Les prédictions ne garantissent aucun gain à la loterie
echo.
echo Pour arrêter le serveur, appuyez sur Ctrl+C
echo.
echo ================================================
echo.

python app.py

pause
