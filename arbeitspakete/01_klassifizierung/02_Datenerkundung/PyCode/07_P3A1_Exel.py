import pandas as pd
import os
from tqdm import tqdm

# Ordner mit Daten
ordner_pfad = "arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
output_excel = "Klassen_Statistiken_gesamt.xlsx"

# Liste für das "Alle_Klassen"-Sheet
all_stats = []

# ExcelWriter öffnen
with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
    for dateiname in tqdm(dateien, desc="Verarbeite Statistik pro Datei"):
        dateipfad = os.path.join(ordner_pfad, dateiname)

        # Daten einlesen
        df = pd.read_csv(dateipfad, delimiter=";", decimal=".", header=None)
        df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
                      "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
                      "X scan dir", "Y scan dir", "Z scan dir",
                      "Hue (°)", "Saturation (%)", "Value (%)"]

        # Statistik berechnen
        stats = df.describe()

        # Klassennamen aus Dateiname ziehen (z. B. "Bäume")
        klasse = dateiname.replace("_HSV.txt", "").split("_")[-1]
        sheet_name = klasse[:31]  # Excel-Sheetname max. 31 Zeichen

        # Speichern als Einzelblatt
        stats.to_excel(writer, sheet_name=sheet_name)

        # In Liste einfügen für zusammengeführtes Sheet
        temp = stats.copy()
        temp["Klasse"] = klasse
        temp.reset_index(inplace=True)
        all_stats.append(temp)

    # Gesamtblatt erstellen
    alle_df = pd.concat(all_stats, ignore_index=True)
    alle_df.to_excel(writer, sheet_name="Alle_Klassen", index=False)

print(f"Excel-Datei '{output_excel}' mit Einzel- und Gesamtsheets wurde erfolgreich erstellt.")
