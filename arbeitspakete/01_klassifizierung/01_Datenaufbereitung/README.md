# 📄 Schritt 01 – 01 Datenaufbereitung

In diesem Ordner werden verschiedene Klassifizierungsansätze dokumentiert.

Generell wichtig ist es das verwenden von printstatements zu implementieren, um den **Prozessfordschritt** anzuzeigen. Das rechnen der Dataframes mit ~10 Spalten und mehreren millionen Zeilen kann einiges an Zeit beanspruchen.

dafür kann mit folgenden **Packages und Codeteilen** gearbeitet werden:

```Python
import time #Zeitmessungen
from tqdm import tqdm #ProgressBar
#---------------------------------

# Startzeit für die Laufzeitmessung
start_time = time.time()

# Arbeitsschritte [..........]
# Fortschrittsbalken für das Speichern der Cluster-Dateien
print("Speichere Cluster-Dateien...")
for cluster_id in tqdm(df["Color Cluster"]):
    #Fortschritt und Zeitausgabe im Terminal pro loop der For-Schleiffe


# Laufzeit berechnen und ausgeben
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")
```
