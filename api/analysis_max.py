
import pandas as pd
import json
import matplotlib.pyplot as plt
df = pd.read_csv("data/processed/tgv_max_departures_cleaned_2025.csv")
df_carcassonne=df[df['destination']=='PARIS (intramuros)']

df_new=df_carcassonne[df_carcassonne["od_happy_card"]=="OUI"]
df_cleaned = df_new.groupby("date").size().reset_index(name="Nb trajets dispos tgv max")


plt.figure(figsize=(10, 6))
plt.plot(df_cleaned["date"], df_cleaned["Nb trajets dispos tgv max"], marker="o", linestyle="-")

plt.title("Nombre de trajets disponibles TGVmax par date", fontsize=14)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Nb trajets non dispos non  TGVmax", fontsize=12)
plt.grid(True)

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()