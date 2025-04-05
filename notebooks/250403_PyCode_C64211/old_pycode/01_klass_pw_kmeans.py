import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
# import open3d as o3d

# TODO Statistik zu der Klassenverteilung machen, zB ein TXT mit Wertebereich zu den Spalten RGB/HSV Werten.
# Link zu Cluster-Algorithmen: https://scikit-learn.org/stable/auto_examples/cluster/index.html
# Link zu Vergleich von Classifier-Algorithmen: https://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html
# Algorithmus DBSCAN könnte sich besser eignen... Density Based Clustering

starttime = time.time()

# Datei mit bereits berechneten HSV-Werten laden
file_path = "PW_KOO_RGB_HSV_norm.txt"  # Falls der Name anders ist, bitte anpassen
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen basierend auf der erweiterten Datei setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# Anzahl der Cluster definieren (zwischen 6 und 10)
num_clusters = 5  # Kann auf 6-10 angepasst werden

# K-Means Clustering auf HSV-Werte anwenden
with tqdm(total=100, desc="Clustering") as pbar:
   kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
#    df["Color Cluster"] = kmeans.fit_predict(df[["Hue (°)", "Saturation (%)", "Value (%)"]])
   df["Color Cluster"] = kmeans.fit_predict(df[["Hue (°)"]])
   pbar.update(100)

# Neue Datei speichern (mit Farbklassen, ohne Header)
output_path = f"PW_{num_clusters}_Klassen_kmeans.txt"
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

print(f"Datei mit KMeans-Farbklassen gespeichert als: {output_path}")

# Erstelle einen Ordner für die Ausgabe (falls nicht vorhanden)
output_folder = f"KMeans_Clustered_Files_{num_clusters}"
os.makedirs(output_folder, exist_ok=True)


# Daten in separate Dateien je Klasse speichern
for cluster_id in tqdm(df["Color Cluster"].unique(), desc="Speichern der Cluster"):
    # Filtere die Punkte für die aktuelle Klasse
    cluster_df = df[df["Color Cluster"] == cluster_id]
    
    # Dateiname für die Klasse
    output_file = os.path.join(output_folder, f"PW_Klasse_{int(cluster_id)}_kmeans.txt")
    
    # Speichern ohne Header
    cluster_df.to_csv(output_file, sep=";", index=False, decimal=".", header=False)

    print(f"Datei gespeichert: {output_file}")

print("Alle KMeans-Cluster-Dateien wurden erfolgreich erstellt!")

endtime = time.time()
total = endtime - starttime
print(f"Total Rechenzeit: {total:.2f} Sekunden")
total = int(total//60)
print(f"Total Rechenzeit: {total:.2f} Minuten")

# # Datei zur Anzeige bringen
# import ace_tools as tools
# tools.display_dataframe_to_user(name="Geklassifizierte Punktwolken-Daten mit KMeans", dataframe=df)

# # Open3D: Punktwolke mit Clustern visualisieren
# points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
# colors = df["Color Cluster"].to_numpy() / num_clusters  # Normieren für Farben

# # Punktwolke für Open3D vorbereiten
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points)
# pcd.colors = o3d.utility.Vector3dVector(plt.cm.jet(colors)[:, :3])  # Farben aus Jet-Colormap

# # Punktwolke anzeigen
# o3d.visualization.draw_geometries([pcd], window_name="Geklassifizierte Punktwolke mit KMeans")
