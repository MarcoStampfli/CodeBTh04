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

# Plot für jede Achse
achsen = {
    "Red color (0-255)": "Rotwerts",
    "Green color (0-255)": "Grünwerts",
    "Blue color (0-255)": "Blauwerts"
}

for spalte, titel in achsen.items():
    plt.figure(figsize=(10, 6))
    ax = sns.kdeplot(
        data=df_gesamt,
        x=spalte,
        hue="Klasse", hue_order=sorted(df_gesamt["Klasse"].unique()),
        common_norm=False,
        fill=False
    )
    plt.xlim(0, 255)
    plt.title(f"Dichteverteilung des {titel} je Klasse")
    plt.xlabel("Farbenwert (0 - 255)")
    plt.ylabel("Dichte")
    ax.legend(title="Klassen", loc="upper left", labels=alle_klassen)

    # Dateiname mit besser lesbarem Titel statt Spaltenname
    dateiname_output = titel.replace("-", "").replace(" ", "")  # z.B. XNormale
    file_path = os.path.join(output_folder, f"Gesamt_{dateiname_output}_Dichte_alle_Klassen.png")
    plt.savefig(file_path, dpi=300)
    plt.close()
    print(f"Gesamtplot gespeichert: {os.path.basename(file_path)}")