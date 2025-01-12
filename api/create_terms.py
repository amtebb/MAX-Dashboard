import csv
from datetime import datetime, timedelta

def generate_periods(start_date, end_date, period="weekly", output_file="terms.csv"):
    """
    Génère un fichier CSV avec des périodes définies (journalières ou hebdomadaires).
    
    Args:
        start_date (str): Date de début au format 'YYYY-MM-DD'.
        end_date (str): Date de fin au format 'YYYY-MM-DD'.
        period (str): Type de période ('daily', 'weekly').
        output_file (str): Nom du fichier de sortie.
    """
    periods = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    final_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current_date <= final_date:
        if period == "daily":
            # Période journalière
            period_end = current_date
        elif period == "weekly":
            # Période hebdomadaire
            period_end = min(current_date + timedelta(days=6), final_date)
        else:
            raise ValueError("Période non supportée : choisissez 'daily' ou 'weekly'")
        
        # Ajouter la période au format string
        periods.append((current_date.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d")))
        
        # Avancer au prochain début de période
        current_date = period_end + timedelta(days=1)
    
    # Écrire les périodes dans un fichier CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["start_date", "end_date"])  # En-têtes
        writer.writerows(periods)
    
    print(f"Fichier {output_file} créé avec {len(periods)} périodes.")

if __name__ == "__main__":
    # Exemple : Créer des périodes hebdomadaires pour 2024 et 2025
    generate_periods("2024-01-01", "2025-12-31", period="weekly", output_file="terms.csv")
