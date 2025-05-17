import pandas as pd
import numpy as np
import os
import time
from tqdm import tqdm
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
# import open3d as o3d

# Startzeit für die Laufzeitmessung
start_time = time.time()

# Datei mit bereits berechneten HSV-Werten laden
file_path = r"C:\Users\st1174360\Documents\BTh_04\250327_Normalisieren\output\PW_P3_normalisiert.txt"  
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen basierend auf der erweiterten Datei setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
            "Red (0-1)", "Green (0-1)", "Blue (0-1)",
            "Hue (0-1)", "Saturation (0-1)", "Value (0-1)",
            "X scan dir", "Y scan dir", "Z scan dir"]

# Anzahl der Cluster definieren
num_clusters = 2  # Kann auf 6-10 angepasst werden
fit = df[["Hue (0-1)"]] # Fit Variablen
fitcode = "H"

# Progressbar für K-Means
print("Starte K-Means Clustering...")
with tqdm(total=100, desc="Clustering") as pbar:
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    df["Color Cluster"] = kmeans.fit_predict(fit)
    pbar.update(100)


# Neue Datei speichern (mit Farbklassen, ohne Header)
output_folder = r"arbeitspakete\01_klassifizierung\05_KMeans\output\KMeans_Clustered_Files"+f"_{num_clusters}_fit_{fitcode}"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, f"kmeans_clustered_{fitcode}_punktwolke.txt")
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

# print(f"Datei mit KMeans-Farbklassen gespeichert als: {output_path}")

# Fortschrittsbalken für das Speichern der Cluster-Dateien
print("Speichere Cluster-Dateien...")
for cluster_id in tqdm(df["Color Cluster"].unique(), desc="Speichern der Cluster"):
    cluster_df = df[df["Color Cluster"] == cluster_id]
    output_file = os.path.join(output_folder, f"PW_Klasse_{int(cluster_id)}_kmeans_fit_{fitcode}.txt")
    cluster_df.to_csv(output_file, sep=";", index=False, decimal=".", header=False)

print("Alle KMeans-Cluster-Dateien wurden erfolgreich erstellt!")

# Laufzeit berechnen und ausgeben
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")

# # Wertebereichs-Datei erstellen
# summary_file = os.path.join(output_folder, "cluster_summary.txt")
# summary_data = []

# print("Berechne Min/Max-Werte für jede Klasse...")
# for cluster_id in tqdm(df["Color Cluster"].unique(), desc="Berechnung"):
#     cluster_df = df[df["Color Cluster"] == cluster_id]
#     min_red, max_red = cluster_df["Red (0-1)"].min(), cluster_df["Red (0-1)"].max()
#     min_green, max_green = cluster_df["Green (0-1)"].min(), cluster_df["Green (0-1)"].max()
#     min_blue, max_blue = cluster_df["Blue (0-1)"].min(), cluster_df["Blue (0-1)"].max()
#     min_hue, max_hue = cluster_df["Hue (0-1)"].min(), cluster_df["Hue (0-1)"].max()
#     min_sat, max_sat = cluster_df["Saturation (0-1)"].min(), cluster_df["Saturation (0-1)"].max()
#     min_val, max_val = cluster_df["Value (0-1)"].min(), cluster_df["Value (0-1)"].max()
#     min_z, max_z = cluster_df["Z scan dir"].min(), cluster_df["Z scan dir"].max()
    
#     summary_data.append([
#         cluster_id,
#         f"[{min_red:.3f}, {max_red:.3f}]",
#         f"[{min_green:.3f}, {max_green:.3f}]",
#         f"[{min_blue:.3f}, {max_blue:.3f}]",
#         f"[{min_hue:.3f}, {max_hue:.3f}]",
#         f"[{min_sat:.3f}, {max_sat:.3f}]",
#         f"[{min_val:.3f}, {max_val:.3f}]",
#         f"[{min_z:.3f}, {max_z:.3f}]"
#     ])
#     summary_df = pd.DataFrame(summary_data, columns=[
#     "KlassNR", "MinMax Red", "MinMax Green", "MinMax Blue", 
#     "MinMax Hue", "MinMax Saturation", "MinMax Value", "MinMax Z"
# ])

# summary_df.to_csv(summary_file, sep=";", index=False, decimal=".")
# print(f"Wertebereichs-Datei gespeichert als: {summary_file}")

# # Open3D: Punktwolke mit Clustern visualisieren
# points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
# colors = df["Color Cluster"].to_numpy() / (df["Color Cluster"].max() + 1)

# # Punktwolke für Open3D vorbereiten
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points)
# pcd.colors = o3d.utility.Vector3dVector(plt.cm.jet(colors)[:, :3])

# # Punktwolke anzeigen
# o3d.visualization.draw_geometries([pcd], window_name="Geklassifizierte Punktwolke mit KMeans")

