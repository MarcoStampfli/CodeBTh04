import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Daten laden (aus deiner Excel-Zusammenfassung)
df = pd.read_excel("SeabornPlots\Klassen_Statistiken_gesamt.xlsx", sheet_name="Alle_Klassen")

# Liste der Spalten, zwischen denen wir Korrelationen betrachten wollen
numerische_spalten = ["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
                      "X scan dir", "Y scan dir", "Z scan dir", 
                      "Hue (°)", "Saturation (%)", "Value (%)"]

# Leere Liste für Ergebnisse
korr_liste = []

# Alle Klassen durchlaufen
for klasse in df["Klasse"].unique():
    df_k = df[df["Klasse"] == klasse][numerische_spalten]
    
    # Korrelation berechnen
    corr = df_k.corr()
    
    # Nur den unteren Dreiecksteil (ohne Diagonale) nehmen
    for i in range(len(corr.columns)):
        for j in range(i):
            val = corr.iloc[i, j]
            name = f"{corr.columns[j]} vs {corr.columns[i]}"
            korr_liste.append({
                "Klasse": klasse,
                "Kombination": name,
                "Korrelation": val
            })

# In DataFrame überführen
korr_df = pd.DataFrame(korr_liste)

# Ausgabeordner
os.makedirs("Violin_Korrelationen", exist_ok=True)

# Violinplot zeichnen
plt.figure(figsize=(14, 6))
sns.violinplot(data=korr_df, x="Klasse", y="Korrelation", bw=0.5, cut=0, palette="Set2")
plt.title("Korrelationen zwischen Merkmalen – Verteilung je Klasse")
plt.xticks(rotation=45)
plt.tight_layout()

# Speichern
plt.savefig("Violin_Korrelationen/Korrelationen_je_Klasse.png", dpi=300)
plt.show()
