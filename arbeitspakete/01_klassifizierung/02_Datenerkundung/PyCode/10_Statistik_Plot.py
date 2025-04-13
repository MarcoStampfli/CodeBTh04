import pandas as pd
import os

# Pfad zum Zielordner
ordnerpfad = r"D:\BTh04_Stadtmodel\Klassen_Statistik"

# Liste relevanter Spalten
relevante_spalten = [
    'Stat',
    'Red color (0-255)',
    'Green color (0-255)',
    'Blue color (0-255)',
    'X scan dir',
    'Y scan dir',
    'Z scan dir',
    'Hue (°)',
    'Saturation (%)',
    'Value (%)'
]

# Leerer DataFrame für die Ergebnisse
alle_statistiken = pd.DataFrame()

# Alle CSV-Dateien im Ordner durchgehen
for dateiname in os.listdir(ordnerpfad):
    if dateiname.endswith("HSV_statistik.csv"):
        dateipfad = os.path.join(ordnerpfad, dateiname)
        
        # CSV-Datei einlesen
        df = pd.read_csv(dateipfad, sep=';', header=None)
        
        # Spaltennamen setzen
        spaltennamen = df.iloc[0].tolist()
        spaltennamen[0] = 'Stat'
        df.columns = spaltennamen
        
        # Nur die Zeilen mit 'mean' und 'std' extrahieren
        df = df[df['Stat'].isin(['mean', 'std'])]
        
        # Nur relevante Spalten behalten
        df = df[relevante_spalten]
        
        # Optional: Dateiname als neue Spalte hinzufügen zur Nachverfolgung
        df['Datei'] = dateiname
        
        # Zur Gesamttabelle hinzufügen
        alle_statistiken = pd.concat([alle_statistiken, df], ignore_index=True)

# Ergebnisse anzeigen oder speichern
print(alle_statistiken)

# Optional: speichern
# alle_statistiken.to_csv("zusammengefasste_statistik.csv", index=False)
