import pandas as pd
import matplotlib.pyplot as plt
import time

# Startzeit für die Laufzeitmessung
start_time = time.time()

# Histo für PW gesamt
# file_path = "PW_KOO_RGB_HSV_norm.txt"

# Histo für PW einzelner Cluster
ClusterNr = 4
NR = 1
file_path = f"KMeans_Clustered_Files_{ClusterNr}\PW_Klasse_{NR}_kmeans.txt"


# Spaltennamen entsprechend der Datei setzen
column_names = ["X coordinate", "Y coordinate", "Z coordinate", 
                "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
                "X scan dir", "Y scan dir", "Z scan dir",
                "Hue (°)", "Saturation (%)", "Value (%)", "Class"]

# Relevante Spalten für die Analyse auswählen
use_columns = ["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
               "Hue (°)", "Saturation (%)", "Value (%)"]

# Datei in Chunks laden (100.000 Zeilen pro Chunk, anpassbar)
chunk_size = 100000
chunks = pd.read_csv(file_path, names=column_names, usecols=use_columns, sep=";", chunksize=chunk_size, decimal=".")

# Daten in einer Liste sammeln
df_list = [chunk for chunk in chunks]

# Alle Chunks in einen DataFrame zusammenfügen
df = pd.concat(df_list, ignore_index=True)

# Small Multiples für die Verteilungen
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Spaltennamen für die Achsentitel
columns = ["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
           "Hue (°)", "Saturation (%)", "Value (%)"]

# Histogramme plotten
for ax, col in zip(axes.flat, columns):
    ax.hist(df[col], bins=50, color="skyblue", edgecolor='black', alpha=0.7)
    ax.set_title(col)
    ax.set_xlabel("Wert")
    ax.set_ylabel("Häufigkeit")

plt.tight_layout()
plt.show()

# Laufzeit berechnen und ausgeben
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")