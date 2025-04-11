import pandas as pd
import os
import time
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

# Zeitmessung starten
start_time = time.time()

# Ordner mit den Eingabedateien
ordner_pfad = "SeabornPlots\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"

# Liste aller .txt-Dateien im Ordner
dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]

output_folder = "Diagramme_clean"
os.makedirs(output_folder, exist_ok=True)

# Progressbar mit tqdm
for dateiname in tqdm(dateien, desc="Verarbeite Dateien"):
    dateipfad = os.path.join(ordner_pfad, dateiname)
    loop_start = time.time()

    klasse = dateiname.split("_")[-2]
    print(klasse)