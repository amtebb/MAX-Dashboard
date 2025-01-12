import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
class TrajetAnalyse:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df_complet = pd.read_csv(file_path, parse_dates=["date"])
        self.nb_pos = 0
        self.nb_neg = 0
        self.calcule_pos_neg()

    def calcule_pos_neg(self):
        df_positive = self.df_complet[self.df_complet["od_happy_card"] == "OUI"]
        df_negative = self.df_complet[self.df_complet["od_happy_card"] == "NON"]
        self.nb_pos = len(df_positive)
        self.nb_neg = len(df_negative)

    def kpi_summary(self):
        """
        Retourne les KPI principaux sous forme de dictionnaire.
        """
        return {
            "total_trajets": self.total,
            "taux_dispo": round(self.pos_rate * 100, 2),
            "taux_indispo": round(self.neg_rate * 100, 2),
            "worth_score": self.worth_score()
        }

    def worth_score(self):
        """
        Calcul d'un score 'worth' basé sur la disponibilité des trajets.
        """
        score = round(self.pos_rate * 100, 2)
        return score

    @property
    def total(self):
        return self.nb_pos + self.nb_neg

    @property
    def pos_rate(self):
        return self.nb_pos / self.total if self.total > 0 else 0

    @property
    def neg_rate(self):
        return self.nb_neg / self.total if self.total > 0 else 0
    
    def plot_month(self, year, month, rep='OUI'):
        """
        Visualise l'évolution journalière des trajets pour un mois donné.

        Args:
            year (int): Année à analyser.
            month (int): Mois à analyser.
            rep (str): Type de trajet à filtrer ('OUI' ou 'NON').

        Returns:
            Figure matplotlib.
        """
        try:
            # Filtrer les données pour l'année et le mois donnés
            filtered_df = self.df_complet[
                (self.df_complet["date"].dt.year == year) &
                (self.df_complet["date"].dt.month == month) &
                (self.df_complet["od_happy_card"] == rep)
            ]

            # Vérifier si le DataFrame filtré n'est pas vide
            if filtered_df.empty:
                raise ValueError(f"Aucune donnée disponible pour {year}-{month:02d} avec 'rep'={rep}.")

            # Compter les trajets par jour
            daily_counts = filtered_df.groupby(filtered_df["date"].dt.day).size()

            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 6))
            daily_counts.plot(kind="line", marker="o", color="skyblue", ax=ax)
            ax.set_title(f"Évolution journalière des trajets '{rep}' ({year}-{month:02d})")
            ax.set_xlabel("Jour")
            ax.set_ylabel("Nombre de trajets")
            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Erreur dans plot_month : {e}")
            raise
    def plot_year(self, year, rep='OUI'):
        """
        Visualise l'évolution mensuelle des trajets pour une année donnée.

        Args:
            year (int): Année à analyser.
            rep (str): Type de trajet à filtrer ('OUI' ou 'NON').

        Returns:
            Figure matplotlib.
        """
        try:
            # Filtrer les données pour l'année donnée
            filtered_df = self.df_complet[
                (self.df_complet["date"].dt.year == year) &
                (self.df_complet["od_happy_card"] == rep)
            ]

            # Vérifier si le DataFrame filtré n'est pas vide
            if filtered_df.empty:
                raise ValueError(f"Aucune donnée disponible pour l'année {year} avec 'rep'={rep}.")

            # Compter les trajets par mois
            monthly_counts = filtered_df.groupby(filtered_df["date"].dt.month).size()

            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 6))
            monthly_counts.plot(kind="bar", color="skyblue", ax=ax)
            ax.set_title(f"Évolution mensuelle des trajets '{rep}' ({year})")
            ax.set_xlabel("Mois")
            ax.set_ylabel("Nombre de trajets")
            ax.set_xticks(range(12))
            ax.set_xticklabels(['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                                'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'])
            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Erreur dans plot_year : {e}")
            raise
