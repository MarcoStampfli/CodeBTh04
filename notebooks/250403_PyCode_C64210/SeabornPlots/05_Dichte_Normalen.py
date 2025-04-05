import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

# Ordner mit den Eingabedateien
ordner_pfad = "SeabornPlots/Klass_Platte_3_Ausschnitt_1/HSV_erweitert"

# Liste aller .txt-Dateien im Ordner
dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]

# Zielordner für Diagramme
output_folder = "Diagramme_clean"
os.makedirs(output_folder, exist_ok=True)

# Leere Liste für kombiniertes DataFrame (alle Klassen)
alle_daten = []
alle_klassen = []

for dateiname in tqdm(dateien, desc="Lese Dateien ein"):
    dateipfad = os.path.join(ordner_pfad, dateiname)
    df = pd.read_csv(dateipfad, delimiter=";", decimal=".", header=None)

    # Spaltennamen setzen
    df.columns = [
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
        "X scan dir", "Y scan dir", "Z scan dir",
        "Hue (°)", "Saturation (%)", "Value (%)"
    ]

    # Klasse aus dem Dateinamen ableiten (z.B. das vorletzte Element vor '_HSV')
    klasse = dateiname.split("_")[-2]  # z.B. "Bäume"
    df["Klasse"] = klasse

    # Hinzufügen zur Gesamtliste
    alle_daten.append(df)
    alle_klassen.append(klasse)


# Alle Daten zu einem DataFrame kombinieren
df_gesamt = pd.concat(alle_daten, ignore_index=True)
# Entferne "Bäume" aus den Daten
# df_gesamt = df_gesamt[df_gesamt["Klasse"] != "Fassade"]

# Plot für jede Achse
achsen = {
    "X scan dir": "X-Normale",
    "Y scan dir": "Y-Normale",
    "Z scan dir": "Z-Normale"
}

for spalte, titel in achsen.items():
    plt.figure(figsize=(10, 6))
    hue_order = df_gesamt["Klasse"]
    ax = sns.kdeplot(
        data=df_gesamt,
        x=spalte,
        hue="Klasse", hue_order=hue_order,
        common_norm=False,
        fill=False
    )
    
    plt.xlim(-1.2, 1.2)
    plt.xticks([-1, 0, 1])
    plt.title(f"Dichteverteilung der {titel} je Klasse")
    plt.xlabel("Normalenwert (-1 bis 1)")
    plt.ylabel("Dichte")
    ax.legend(title="Klassen", loc="upper left",labels= hue_order)

    dateiname_output = titel.replace("-", "").replace(" ", "")
    file_path = os.path.join(output_folder, f"Gesamt_{dateiname_output}_Dichte_alle_Klassen2.png")
    plt.savefig(file_path, dpi=300)
    plt.close()
    print(f"Gesamtplot gespeichert: {os.path.basename(file_path)}")
