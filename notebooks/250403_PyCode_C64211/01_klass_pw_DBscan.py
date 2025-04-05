import pandas as pd
import numpy as np
import os
import time
from tqdm import tqdm
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
# import open3d as o3d

# Startzeit für die Laufzeitmessung
start_time = time.time()

# Datei mit bereits berechneten HSV-Werten laden
file_path = "PW_KOO_RGB_HSV_norm.txt"  # Falls der Name anders ist, bitte anpassen
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen basierend auf der erweiterten Datei setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# DBSCAN Parameter definieren
eps = 10  # Maximale Distanz zwischen zwei Punkten, damit sie im gleichen Cluster sind
min_samples = 10000  # Mindestanzahl an Punkten in einem Cluster => ANZ POINTS 42 MIO

# Progressbar für DBSCAN
print("Starte DBSCAN Clustering...")
with tqdm(total=100, desc="Clustering") as pbar:
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    df["Color Cluster"] = dbscan.fit_predict(df[["Hue (°)", "Saturation (%)", "Value (%)"]])
    pbar.update(100)

# Neue Datei speichern (mit Farbklassen, ohne Header)
output_path = "dbscan_clustered_punktwolke.txt"
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

print(f"Datei mit DBSCAN-Farbklassen gespeichert als: {output_path}")

# Erstelle einen Ordner für die Ausgabe (falls nicht vorhanden)
output_folder = f"DBSCAN_Clustered_Files_Dist={eps}_Samp={min_samples}"
os.makedirs(output_folder, exist_ok=True)

# Fortschrittsbalken für das Speichern der Cluster-Dateien
print("Speichere Cluster-Dateien...")
for cluster_id in tqdm(df["Color Cluster"].unique(), desc="Speichern der Cluster"):
    # Filtere die Punkte für die aktuelle Klasse
    cluster_df = df[df["Color Cluster"] == cluster_id]
    
    # Dateiname für die Klasse
    output_file = os.path.join(output_folder, f"PW_Klasse_{int(cluster_id)}_dbscan.txt")
    
    # Speichern ohne Header
    cluster_df.to_csv(output_file, sep=";", index=False, decimal=".", header=False)

print("Alle DBSCAN-Cluster-Dateien wurden erfolgreich erstellt!")

# Laufzeit berechnen und ausgeben
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")

# # Datei zur Anzeige bringen
# import ace_tools as tools
# tools.display_dataframe_to_user(name="Geklassifizierte Punktwolken-Daten mit DBSCAN", dataframe=df)

# Wertebereichs-Datei erstellen
summary_file = os.path.join(output_folder, "cluster_summary.txt")
summary_data = []

print("Berechne Min/Max-Werte für jede Klasse...")
for cluster_id in tqdm(df["Color Cluster"].unique(), desc="Berechnung"):
    cluster_df = df[df["Color Cluster"] == cluster_id]
    
    min_red, max_red = cluster_df["Red color (0-255)"].min(), cluster_df["Red color (0-255)"].max()
    min_green, max_green = cluster_df["Green color (0-255)"].min(), cluster_df["Green color (0-255)"].max()
    min_blue, max_blue = cluster_df["Blue color (0-255)"].min(), cluster_df["Blue color (0-255)"].max()
    min_hue, max_hue = cluster_df["Hue (°)"].min(), cluster_df["Hue (°)"].max()
    min_sat, max_sat = cluster_df["Saturation (%)"].min(), cluster_df["Saturation (%)"].max()
    min_val, max_val = cluster_df["Value (%)"].min(), cluster_df["Value (%)"].max()
    
    summary_data.append([
        cluster_id,
        f"[{min_red}, {max_red}]", f"[{min_green}, {max_green}]", f"[{min_blue}, {max_blue}]",
        f"[{min_hue}, {max_hue}]", f"[{min_sat}, {max_sat}]", f"[{min_val}, {max_val}]"
    ])

summary_df = pd.DataFrame(summary_data, columns=[
    "KlassNR", "MinMax Red", "MinMax Green", "MinMax Blue", 
    "MinMax Hue", "MinMax Saturation", "MinMax Value"
])

summary_df.to_csv(summary_file, sep=";", index=False, decimal=".")

print(f"Wertebereichs-Datei gespeichert als: {summary_file}")

# # Open3D: Punktwolke mit Clustern visualisieren
# points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
# colors = df["Color Cluster"].to_numpy() / (df["Color Cluster"].max() + 1)  # Normieren für Farben

# # Punktwolke für Open3D vorbereiten
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points)
# pcd.colors = o3d.utility.Vector3dVector(plt.cm.jet(colors)[:, :3])  # Farben aus Jet-Colormap

# # Punktwolke anzeigen
# o3d.visualization.draw_geometries([pcd], window_name="Geklassifizierte Punktwolke mit DBSCAN")
