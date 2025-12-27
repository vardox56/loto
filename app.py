##################################################################
# app.py: Flask API pour le système de prédiction Loto
##################################################################

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from bs4 import BeautifulSoup
import time
import requests
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

##################################################################
# Configuration
##################################################################
pairs = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50]
impairs = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49]

nb_label_feature = 6
UNITS = 100
BATCHSIZE = 30
EPOCH = 1000
OPTIMIZER = 'adam'
LOSS = 'mae'
DROPOUT = 0.1
window_length = 12

##################################################################
# Fonctions de scraping et traitement
##################################################################
def scrap_loto_numbers():
    """Récupère les données historiques du loto"""
    my_list = []
    time.sleep(2)
    loto_url = "http://loto.akroweb.fr/loto-historique-tirages/"
    
    try:
        page = requests.get(loto_url, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')
        body = soup.find('table')
        tirage_line = body.find_all('tr')
        
        for value in tirage_line:
            my_dict = {}
            res = value.text.split('\n')
            
            if len(res) < 11:
                continue
                
            my_dict['day'] = res[2]
            my_dict['month_year'] = res[3]
            
            for i, val in enumerate(res[5:10]):
                my_dict['num' + str(i)] = int(val)
            
            my_dict['chance'] = int(res[10])
            my_list.append(my_dict)
        
        df = pd.DataFrame(my_list)
        return df
    except Exception as e:
        print(f"Erreur lors du scraping: {e}")
        return None

def freq_val(data, column):
    """Calcule la fréquence de chaque valeur"""
    tab = data[column].values.tolist()
    freqs = []
    pos = 1
    for e in tab:
        freqs.append(tab[0:pos].count(e))
        pos = pos + 1
    return freqs

def is_under(data, number):
    """Compte combien de numéros sont sous une valeur donnée"""
    return ((data['num0'] <= number).astype(int) +
            (data['num1'] <= number).astype(int) +
            (data['num2'] <= number).astype(int) +
            (data['num3'] <= number).astype(int) +
            (data['num4'] <= number).astype(int))

def is_pair(data):
    """Compte les numéros pairs"""
    return ((data['num0'].isin(pairs)).astype(int) +
            (data['num1'].isin(pairs)).astype(int) +
            (data['num2'].isin(pairs)).astype(int) +
            (data['num3'].isin(pairs)).astype(int) +
            (data['num4'].isin(pairs)).astype(int))

def is_impair(data):
    """Compte les numéros impairs"""
    return ((data['num0'].isin(impairs)).astype(int) +
            (data['num1'].isin(impairs)).astype(int) +
            (data['num2'].isin(impairs)).astype(int) +
            (data['num3'].isin(impairs)).astype(int) +
            (data['num4'].isin(impairs)).astype(int))

def is_pair_etoile(data):
    """Vérifie si le numéro chance est pair"""
    return (data['chance'].isin(pairs)).astype(int)

def is_impair_etoile(data):
    """Vérifie si le numéro chance est impair"""
    return (data['chance'].isin(impairs)).astype(int)

def sum_diff(data):
    """Calcule la somme des différences au carré"""
    return ((data['num1'] - data['num0']) ** 2 +
            (data['num2'] - data['num1']) ** 2 +
            (data['num3'] - data['num2']) ** 2 +
            (data['num4'] - data['num3']) ** 2)

def calculate_mean(data):
    """Moyenne des numéros"""
    return data[['num0', 'num1', 'num2', 'num3', 'num4']].mean(axis=1)

def calculate_median(data):
    """Médiane des numéros"""
    return data[['num0', 'num1', 'num2', 'num3', 'num4']].median(axis=1)

def calculate_std(data):
    """Écart-type des numéros"""
    return data[['num0', 'num1', 'num2', 'num3', 'num4']].std(axis=1)

def calculate_range(data):
    """Plage (max - min) des numéros"""
    return data[['num0', 'num1', 'num2', 'num3', 'num4']].max(axis=1) - data[
        ['num0', 'num1', 'num2', 'num3', 'num4']].min(axis=1)

def sum_numbers(data):
    """Somme des numéros"""
    return data[['num0', 'num1', 'num2', 'num3', 'num4']].sum(axis=1)

def odd_even_ratio(data):
    """Ratio impairs/pairs"""
    odd_count = (data[['num0', 'num1', 'num2', 'num3', 'num4']] % 2).sum(axis=1)
    even_count = 5 - odd_count
    return odd_count / (even_count + 0.001)  # Éviter division par zéro

def preprocess_data(df):
    """Applique le feature engineering complet"""
    df = df.iloc[::-1]
    df = df[['num0', 'num1', 'num2', 'num3', 'num4', 'chance']]
    
    # Feature engineering
    df['freq_num0'] = freq_val(df, 'num0')
    df['freq_num1'] = freq_val(df, 'num1')
    df['freq_num2'] = freq_val(df, 'num2')
    df['freq_num3'] = freq_val(df, 'num3')
    df['freq_num4'] = freq_val(df, 'num4')
    df['freq_chance'] = freq_val(df, 'chance')
    df['sum_diff'] = sum_diff(df)
    df['pair_chance'] = is_pair_etoile(df)
    df['impair_chance'] = is_impair_etoile(df)
    df['pair'] = is_pair(df)
    df['impair'] = is_impair(df)
    df['is_under_24'] = is_under(df, 24)
    df['is_under_40'] = is_under(df, 40)
    df['mean'] = calculate_mean(df)
    df['median'] = calculate_median(df)
    df['std'] = calculate_std(df)
    df['range'] = calculate_range(df)
    df['sum'] = sum_numbers(df)
    df['odd_even_ratio'] = odd_even_ratio(df)
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    
    return df

def define_model(number_of_features, nb_label_feature):
    """Définit le modèle LSTM"""
    model = Sequential()
    model.add(LSTM(UNITS, input_shape=(window_length, number_of_features), return_sequences=True))
    model.add(LSTM(UNITS, dropout=0.1, return_sequences=False))
    model.add(Dense(nb_label_feature))
    model.compile(loss=LOSS, optimizer=OPTIMIZER, metrics=['acc'])
    return model

def create_lstm_dataset(df, window_length, nb_label_feature):
    """Crée le dataset pour LSTM"""
    number_of_rows = df.shape[0]
    number_of_features = df.shape[1]
    
    scaler = StandardScaler().fit(df.values)
    transformed_dataset = scaler.transform(df.values)
    transformed_df = pd.DataFrame(data=transformed_dataset, index=df.index)

    train = np.empty([number_of_rows - window_length, window_length, number_of_features], dtype=float)
    label = np.empty([number_of_rows - window_length, nb_label_feature], dtype=float)
    
    for i in range(0, number_of_rows - window_length):
        train[i] = transformed_df.iloc[i:i + window_length, 0: number_of_features].values
        label[i] = transformed_df.iloc[i + window_length: i + window_length + 1, 0:nb_label_feature].values

    return train, label, scaler

##################################################################
# Routes API
##################################################################
@app.route('/')
def index():
    """Sert la page principale"""
    return send_from_directory('static', 'index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    """Génère une prédiction basée sur le modèle LSTM"""
    try:
        # Récupération des données
        data = request.get_json()
        retrain = data.get('retrain', False)
        strategy = data.get('strategy', 'balanced')  # balanced, uncommon, random
        
        # Scraping des données
        df_tirage = scrap_loto_numbers()
        if df_tirage is None:
            return jsonify({'error': 'Impossible de récupérer les données'}), 500
        
        # Prétraitement
        df = preprocess_data(df_tirage)
        
        # Analyser les combinaisons les moins jouées
        all_numbers = []
        for col in ['num0', 'num1', 'num2', 'num3', 'num4']:
            all_numbers.extend(df_tirage[col].tolist())
        
        # Calculer la fréquence de chaque numéro
        freq_dict = {}
        for num in range(1, 50):
            freq_dict[num] = all_numbers.count(num)
        
        # Stratégies de sélection
        if strategy == 'uncommon':
            # Stratégie 1 : Numéros les MOINS fréquents (moins joués par les autres)
            sorted_nums = sorted(freq_dict.items(), key=lambda x: x[1])
            # Prendre parmi les 30 moins fréquents
            candidates = [n for n, _ in sorted_nums[:30]]
            predictions = []
            
            # Sélection équilibrée
            pairs = [n for n in candidates if n % 2 == 0]
            impairs = [n for n in candidates if n % 2 != 0]
            bas = [n for n in candidates if n <= 24]
            haut = [n for n in candidates if n > 24]
            
            # 2-3 pairs, 2-3 impairs
            predictions.extend(np.random.choice(pairs, size=min(3, len(pairs)), replace=False).tolist())
            predictions.extend(np.random.choice(impairs, size=min(2, len(impairs)), replace=False).tolist())
            
            # Compléter si nécessaire
            while len(predictions) < 5:
                new_num = np.random.choice(candidates)
                if new_num not in predictions:
                    predictions.append(int(new_num))
            
            predictions = sorted(predictions[:5])
            
        elif strategy == 'balanced':
            # Stratégie 2 : Équilibre mathématique optimal
            predictions = []
            
            # 2-3 pairs, 2-3 impairs
            pairs = np.random.choice([n for n in range(2, 50, 2)], size=3, replace=False)
            impairs = np.random.choice([n for n in range(1, 50, 2)], size=2, replace=False)
            
            predictions.extend(pairs.tolist())
            predictions.extend(impairs.tolist())
            predictions = sorted(predictions)
            
            # Éviter les patterns évidents
            # Vérifier qu'il n'y a pas 3+ numéros consécutifs
            consecutive = 0
            for i in range(len(predictions) - 1):
                if predictions[i + 1] - predictions[i] == 1:
                    consecutive += 1
                    if consecutive >= 2:
                        # Remplacer le dernier numéro
                        new_num = np.random.randint(1, 50)
                        while new_num in predictions or (new_num - 1 in predictions and new_num + 1 in predictions):
                            new_num = np.random.randint(1, 50)
                        predictions[-1] = new_num
                        predictions = sorted(predictions)
                        break
                else:
                    consecutive = 0
            
        else:
            # Stratégie 3 : Utiliser le modèle LSTM (pour les curieux)
            train, label, scaler = create_lstm_dataset(df, window_length, nb_label_feature)
            
            model_path = 'best_model.keras'
            if os.path.exists(model_path) and not retrain:
                best_model = load_model(model_path)
            else:
                best_model = define_model(train.shape[2], nb_label_feature)
                
                if retrain:
                    checkpoint_callback = ModelCheckpoint(
                        filepath=model_path,
                        monitor='val_loss',
                        save_best_only=True,
                        verbose=0
                    )
                    
                    best_model.fit(
                        train,
                        label,
                        batch_size=BATCHSIZE,
                        epochs=EPOCH,
                        verbose=0,
                        validation_split=0.2,
                        callbacks=[
                            EarlyStopping(monitor='val_loss', mode='min', patience=200),
                            checkpoint_callback
                        ]
                    )
            
            last_twelve = df.tail(window_length)
            scaled_to_predict = scaler.transform(last_twelve.values)
            scaled_predicted_output = best_model.predict(np.array([scaled_to_predict]), verbose=0)
            
            placeholder = np.zeros((1, df.shape[1]))
            placeholder[0, :6] = scaled_predicted_output
            original_scale_pred = scaler.inverse_transform(placeholder)
            
            predictions = original_scale_pred[0, :6].astype(int)
            predictions = np.clip(predictions, 1, 49)
            predictions = sorted(list(set(predictions)))
            
            while len(predictions) < 5:
                new_num = np.random.randint(1, 50)
                if new_num not in predictions:
                    predictions.append(new_num)
            
            predictions = sorted(predictions[:5])
        
        # Convertir en int Python natif pour JSON
        predictions = [int(x) for x in predictions]
        
        # Générer le numéro chance (éviter 7, 5, 3 qui sont trop joués)
        uncommon_chances = [1, 2, 4, 6, 8, 9, 10]
        chance = int(np.random.choice(uncommon_chances))
        
        # Statistiques (convertir en types Python natifs)
        stats = {
            'pairs': int(sum(1 for n in predictions if n % 2 == 0)),
            'impairs': int(sum(1 for n in predictions if n % 2 != 0)),
            'bas': int(sum(1 for n in predictions if n <= 24)),
            'haut': int(sum(1 for n in predictions if n > 24)),
            'somme': int(sum(predictions)),
            'moyenne': float(round(np.mean(predictions), 2)),
            'ecart': int(max(predictions) - min(predictions))
        }
        
        # Calculer le taux de recouvrement (% de combinaisons couvertes)
        num_grids = 1
        total_combinations = 1906884
        coverage = (num_grids / total_combinations) * 100
        real_probability = f"1 sur {total_combinations:,}".replace(',', ' ')
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'chance': chance,
            'stats': stats,
            'timestamp': datetime.now().isoformat(),
            'model_status': 'optimized',
            'strategy': strategy,
            'probability': real_probability,
            'coverage': coverage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Récupère l'historique des tirages"""
    try:
        df_tirage = scrap_loto_numbers()
        if df_tirage is None:
            return jsonify({'error': 'Impossible de récupérer les données'}), 500
        
        # Prendre les 20 derniers tirages
        recent = df_tirage.head(20)
        
        history = []
        for _, row in recent.iterrows():
            history.append({
                'date': f"{row['day']} {row['month_year']}",
                'numbers': [int(row['num0']), int(row['num1']), int(row['num2']), int(row['num3']), int(row['num4'])],
                'chance': int(row['chance'])
            })
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Calcule les statistiques globales"""
    try:
        df_tirage = scrap_loto_numbers()
        if df_tirage is None:
            return jsonify({'error': 'Impossible de récupérer les données'}), 500
        
        # Statistiques sur les numéros
        all_numbers = []
        for col in ['num0', 'num1', 'num2', 'num3', 'num4']:
            all_numbers.extend(df_tirage[col].tolist())
        
        # Fréquence des numéros
        freq_dict = {}
        for num in range(1, 50):
            freq_dict[num] = all_numbers.count(num)
        
        # Top 10 numéros les plus fréquents
        top_numbers = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Statistiques globales
        stats = {
            'total_tirages': int(len(df_tirage)),
            'top_numbers': [{'number': int(n), 'frequency': int(f)} for n, f in top_numbers],
            'pairs_avg': float(round(np.mean([is_pair(df_tirage).mean()]) * 5, 2)),
            'impairs_avg': float(round(np.mean([is_impair(df_tirage).mean()]) * 5, 2))
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Créer le dossier static s'il n'existe pas
    os.makedirs('static', exist_ok=True)
    
    # Lancer le serveur
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)


