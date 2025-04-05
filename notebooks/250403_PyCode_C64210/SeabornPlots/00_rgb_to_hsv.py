import pandas as pd
import colorsys
import os
import time
from tqdm import tqdm

# Zeitmessung starten
start_time = time.time()

# Ordner mit den Eingabedateien
ordner_pfad = "SeabornPlots\Klass_Platte_3_Ausschnitt_1"

# Optional: Ausgabe in separatem Unterordner speichern
output_ordner = os.path.join(ordner_pfad, "HSV_erweitert")
os.makedirs(output_ordner, exist_ok=True)

# Liste aller .txt-Dateien im Ordner
dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]

# Progressbar mit tqdm
for dateiname in tqdm(dateien, desc="Verarbeite Dateien"):
    dateipfad = os.path.join(ordner_pfad, dateiname)

    # Datei einlesen
    df = pd.read_csv(dateipfad, delimiter=";", decimal=".", header=None)

    # Spaltennamen setzen
    df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
                  "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
                  "X scan dir", "Y scan dir", "Z scan dir"]

    # RGB → HSV Umwandlung
    def rgb_to_hsv(row):
        r, g, b = row["Red color (0-255)"], row["Green color (0-255)"], row["Blue color (0-255)"]
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return pd.Series([h * 360, s * 100, v * 100])

    df[["Hue (°)", "Saturation (%)", "Value (%)"]] = df.apply(rgb_to_hsv, axis=1)

    # Neuer Dateiname
    neuer_name = dateiname.replace(".txt", "_HSV.txt")
    output_path = os.path.join(output_ordner, neuer_name)

    # Speichern ohne Header
    df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

# Zeitmessung beenden
end_time = time.time()
dauer = end_time - start_time
print(f"\n✅ Fertig! Alle Dateien wurden erweitert und gespeichert.")
print(f"⏱️ Dauer: {dauer:.2f} Sekunden")
print(f"📂 Ergebnisse liegen in: {output_ordner}")
