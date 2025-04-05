import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Excel-Sheet laden
df = pd.read_excel("SeabornPlots\Klassen_Statistiken_gesamt.xlsx", sheet_name="Alle_Klassen")

# Nur Zeilen mit Einzelwerten (nicht count, mean etc.) verwenden
df_data = df[df["index"].isin(["min", "25%", "50%", "75%", "max"]) == False]

# merkmale = ["Z scan dir", "Hue (°)", "Red color (0-255)"]

# for merkmal in merkmale:
#     plt.figure(figsize=(8, 6))
#     sns.boxplot(data=df_data, y="Klasse", x=merkmal, orient="h", width=0.6)
#     plt.title(f"Boxplot von '{merkmal}' je Klasse")
#     plt.xlabel(merkmal)
#     plt.ylabel("Klasse")
#     plt.tight_layout()
#     plt.savefig(f"Boxplot_{merkmal.replace(' ', '_')}_horizontal.png", dpi=300)
#     plt.close()
