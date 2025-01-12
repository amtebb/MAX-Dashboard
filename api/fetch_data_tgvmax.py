import requests
import os
import pandas as pd
from datetime import datetime

# URL de l'API
API_URL = "https://ressources.data.sncf.com/api/records/1.0/search/"
DATASET_ID = "tgvmax"

def fetch_unique_stations():
    """
    Récupère la liste des gares uniques depuis l'API SNCF.

    Returns:
        list: Liste des noms de gares uniques triés par ordre alphabétique.
    """
    try:
        # Paramètres pour récupérer un échantillon de toutes les gares
        params = {
            "dataset": DATASET_ID,
            "rows": 1000,  # Nombre maximal d'enregistrements
            "facet": "origine"  # Facette pour grouper par origine
        }

        # Requête API
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extraire les gares uniques
        records = data.get("facet_groups", [])
        if records:
            stations = [facet["name"] for facet in records[0]["facets"]]
            return sorted(set(stations))  # Supprime les doublons et trie
        else:
            print("Aucune donnée trouvée dans l'API.")
            return []
    except Exception as e:
        print(f"Erreur lors de la récupération des gares : {e}")
        return []
def fetch_data_with_csv_cache(
    départ, arrivée, term_file="api/terms.csv", cache_folder="dashboard/data/cache", cache_log="dashboard/data/cache_log.csv"
):
    """
    Récupère les données TGVmax pour une paire départ/arrivée en utilisant un cache CSV.
    Met à jour uniquement les données manquantes dans le cache.

    Args:
        départ (str): Ville de départ.
        arrivée (str): Ville d'arrivée.
        term_file (str): Chemin du fichier CSV contenant les périodes (start_date, end_date).
        cache_folder (str): Dossier où sauvegarder les fichiers CSV par départ/arrivée.
        cache_log (str): Fichier CSV central qui garde une trace des dernières dates enregistrées.

    Returns:
        str: Chemin du fichier cache si des données ont été sauvegardées, sinon None.
    """
    rows_per_request = 1000  # Nombre de lignes par requête API

    # Créer le dossier de cache s'il n'existe pas
    os.makedirs(cache_folder, exist_ok=True)

    # Charger ou initialiser le fichier de log du cache
    if os.path.exists(cache_log):
        cache_df = pd.read_csv(cache_log)
    else:
        cache_df = pd.DataFrame(columns=["départ", "arrivée", "dernière_date"])

    # Vérifier si la paire départ/arrivée existe dans le fichier de log
    cache_entry = cache_df[(cache_df["départ"] == départ) & (cache_df["arrivée"] == arrivée)]
    last_date_in_cache = None

    if not cache_entry.empty:
        last_date_in_cache = pd.to_datetime(cache_entry.iloc[0]["dernière_date"])

    # Lire les périodes depuis le fichier CSV
    if not os.path.exists(term_file):
        raise FileNotFoundError(f"Le fichier {term_file} est introuvable.")
    
    terms = pd.read_csv(term_file)
    terms['start_date'] = pd.to_datetime(terms['start_date'])
    terms['end_date'] = pd.to_datetime(terms['end_date'])

    # Limiter les périodes à un maximum de 2 mois à partir d'aujourd'hui
    today = pd.Timestamp.today()
    max_end_date = today + pd.DateOffset(months=2)
    cache_file = os.path.join(cache_folder, f"{départ.replace(' ', '_')}_to_{arrivée.replace(' ', '_')}.csv")
    
    all_data = []  # Pour collecter toutes les nouvelles données
    
    for _, row in terms.iterrows():
        start_date = row['start_date']
        end_date = row['end_date']

        # Limiter end_date à max_end_date
        if end_date > max_end_date:
            end_date = max_end_date

        # Ignorer les périodes qui commencent avant aujourd'hui
        if start_date < today:
            start_date = today

        # Ajuster la période en fonction des données en cache
        if last_date_in_cache and last_date_in_cache >= start_date:
            start_date = last_date_in_cache + pd.Timedelta(days=1)
            if start_date > end_date:
                print(f"Données déjà à jour pour {départ} -> {arrivée}")
                continue

        print(f"Récupération des données pour {départ} -> {arrivée} (de {start_date} à {end_date})")

        # Récupérer les données manquantes
        start_index = 0

        while True:
            params = {
                "dataset": DATASET_ID,
                "rows": rows_per_request,
                "start": start_index,
                "sort": "date",
                "q": f"origine = '{départ}' AND destination = '{arrivée}' AND date >= '{start_date.strftime('%Y-%m-%d')}' AND date <= '{end_date.strftime('%Y-%m-%d')}'"
            }

            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            records = data.get("records", [])
            if not records:
                break

            all_data.extend([record["fields"] for record in records])
            start_index += rows_per_request

            if len(records) < rows_per_request:
                break

    # Sauvegarder les nouvelles données dans un fichier CSV si des données ont été récupérées
    if all_data:
        new_data_df = pd.DataFrame(all_data)

        if os.path.exists(cache_file):
            existing_data_df = pd.read_csv(cache_file)
            new_data_df = pd.concat([existing_data_df, new_data_df]).drop_duplicates()

        new_data_df.to_csv(cache_file, index=False)
        print(f"Enregistré {len(new_data_df)} lignes dans {cache_file}")

        # Mettre à jour la dernière date dans le fichier de log
        last_date = new_data_df["date"].max()

        if cache_entry.empty:
            # Ajouter une nouvelle entrée si la paire n'existe pas
            new_entry = pd.DataFrame([{"départ": départ, "arrivée": arrivée, "dernière_date": last_date}])
            cache_df = pd.concat([cache_df, new_entry], ignore_index=True)
        else:
            # Mettre à jour l'entrée existante
            cache_df.loc[(cache_df["départ"] == départ) & (cache_df["arrivée"] == arrivée), "dernière_date"] = last_date

        # Sauvegarder le fichier de log mis à jour
        cache_df.to_csv(cache_log, index=False)
        print(f"Fichier de log mis à jour : {cache_log}")
        return cache_file
    else:
        print(f"Aucune donnée supplémentaire récupérée pour {départ} -> {arrivée}")
        return None
