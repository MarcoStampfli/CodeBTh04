import pandas as pd
import os
import time
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

# Zeitmessung starten
start_time = time.time()

# Eingabe- und Ausgabeordner
ordner_pfad = r"SeabornPlots/Klass_Platte_3_Ausschnitt_1/HSV_erweitert"
output_folder = "Klassen_Statistik"
os.makedirs(output_folder, exist_ok=True)

# Alle .txt-Dateien sammeln
dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]

# Progressbar
for dateiname in tqdm(dateien, desc="Verarbeite Dateien"):
    loop_start = time.time()
    dateipfad = os.path.join(ordner_pfad, dateiname)

    # Einlesen
    df = pd.read_csv(dateipfad, delimiter=";", decimal=".", header=None)

    df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
                  "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
                  "X scan dir", "Y scan dir", "Z scan dir",
                  "Hue (°)", "Saturation (%)", "Value (%)"]

    # Statistik berechnen
    statistik = df.describe()
    output_csv = os.path.join(output_folder, dateiname.replace(".txt", "_statistik.csv"))
    statistik.to_csv(output_csv, sep=";", decimal=".")

    # Korrelation als CSV speichern
    correlation = df.corr(numeric_only=True)
    corr_path = os.path.join(output_folder, dateiname.replace(".txt", "_korrelation.csv"))
    correlation.to_csv(corr_path, sep=";", decimal=".")

    # Optional: Korrelation als Heatmap speichern
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title(f"Korrelationsmatrix: {dateiname}")
    heatmap_path = os.path.join(output_folder, dateiname.replace(".txt", "_korrelation.png"))
    plt.savefig(heatmap_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Zeitmessung pro Datei
    loop_end = time.time()
    h, r = divmod(loop_end - loop_start, 3600)
    m, s = divmod(r, 60)
    print(f"Dauer für {dateiname}: {int(h):02d}:{int(m):02d}:{int(s):02d} (hh:mm:ss)\n")

# Gesamtzeit
end_time = time.time()
h, r = divmod(end_time - start_time, 3600)
m, s = divmod(r, 60)
print(f"Alle Dateien verarbeitet.")
print(f"Gesamtdauer: {int(h):02d}:{int(m):02d}:{int(s):02d} (hh:mm:ss)")
