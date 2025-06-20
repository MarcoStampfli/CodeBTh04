# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
"""
Abstract:
Dieses Skript segmentiert und analysiert Einzelbäume aus einer urbanen Punktwolke (z. B. LiDAR) mittels DBSCAN-Clustering und 
extrahiert grundlegende Baumparameter wie Position, Höhe und Kronendurchmesser. Für jedes Cluster wird ein konvexer Rumpf berechnet, 
aus dem die Kronendimensionen abgeleitet werden. Die Ergebnisse werden als CSV-Datei gespeichert. Zusätzlich erzeugt das Skript 
verschiedene 3D-Visualisierungen: Die Punktwolke wird farblich nach Clustern und Noise unterschieden, Baumzentren werden als Sphären markiert, 
und Screenshots der Szenen werden automatisiert gespeichert. Die Visualisierung erfolgt interaktiv mit Open3D und dient der 
schnellen Qualitätskontrolle der Segmentierungsergebnisse.
"""

import os
import time
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
import open3d as o3d
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from tqdm import tqdm

# ------------------------------------------------------------
# BTH 04 Stadtmodell Basel -- Ansatz 1 Segmentierung der Bäume
# ------------------------------------------------------------
"""
Code wurde mit Hilfe von ChatGpt erstellt.
"""


# Label für Ausgabe
RunId = 250510_2
# -------------------------------------------
# Parameterdefinition (Tuningmöglichkeiten)
# -------------------------------------------
eps = 2             # DBSCAN: Radius
min_samples = 300      # DBSCAN: Mindestpunkte pro Cluster
radius = 3             # Sphärengrössen der Visualisierung


# ----------------------
# 0. Startzeit & Output
# ----------------------
start_time = time.time()
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\output"
os.makedirs(output_dir, exist_ok=True)
print(f"\n Output-Ordner: {output_dir}")

# ----------------------
# 1. Punktwolke laden
# ----------------------
print(" Lade Punktwolke ...")
txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\PW_Baeume_o_Boden_o_Rauschen.txt"
df_txt = pd.read_csv(txt_path, delimiter=";", decimal=".", header=None)
df_txt.columns = ['X', 'Y', 'Z']
points = df_txt[['X', 'Y', 'Z']].values

# Optional: Filterung unterhalb 2 m (nur Baumkronen)
vegetation = points[points[:, 2] > 2.0]
print(f" Gefilterte Punkte >2m: {vegetation.shape[0]}")

# ----------------------
# 2. DBSCAN-Clustering
# ----------------------
print(" Starte DBSCAN-Clustering ...")
db = DBSCAN(eps=eps, min_samples=min_samples)  # eps = Nachbarschaftsradius in m
labels = db.fit_predict(vegetation)
vegetation_with_labels = np.hstack((vegetation, labels[:, np.newaxis]))

unique_labels = np.unique(labels)
n_clusters = len(unique_labels[unique_labels != -1])
print(f"🌳 Gefundene Cluster (Bäume): {n_clusters}")

# ----------------------
# 3. Clusteranalyse
# ----------------------
print(" Berechne Baumdaten ...")
tree_data = []
for label in tqdm(unique_labels, desc="Analysiere Cluster"):
    if label == -1:
        continue  # Noise
    cluster_points = vegetation_with_labels[vegetation_with_labels[:, 3] == label][:, :3]

    z_min = np.min(cluster_points[:, 2])
    z_max = np.max(cluster_points[:, 2])
    height = z_max - z_min

    try:
        hull = ConvexHull(cluster_points[:, :2])
        area = hull.area
        diameter = np.sqrt(4 * area / np.pi)
    except:
        diameter = np.nan  # Falls ConvexHull fehlschlägt

    centroid = np.mean(cluster_points, axis=0)

    tree_data.append({
        "Tree_ID": int(label),
        "X": centroid[0],
        "Y": centroid[1],
        "Z": centroid[2],
        "Height_m": round(height, 2),
        "Crown_Diameter_m": round(diameter, 2)
    })

df = pd.DataFrame(tree_data)
csv_path = os.path.join(output_dir, f"baum_cluster_ID_{RunId}.csv")
df.to_csv(csv_path, index=False)
print(f"💾 CSV gespeichert: {csv_path}")

# ----------------------
# 4. Visualisierung vorbereiten
# ----------------------
print(" Erzeuge Open3D-Objekte ...")
colors = plt.colormaps["tab20"] 
vis_colors = np.zeros((vegetation.shape[0], 3))

for i, label in enumerate(labels):
    if label == -1:
        vis_colors[i] = [0.5, 0.5, 0.5]  # Grau für Noise
    else:
        vis_colors[i] = colors(label % 20)[:3]

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(vegetation)
pcd.colors = o3d.utility.Vector3dVector(vis_colors)

# Baumzentren als Kugeln
print(" Erzeuge Baum-Sphären ...")
sphere_list = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Sphären erzeugen"):
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
    sphere.translate([row["X"], row["Y"], row["Z"]])
    sphere.paint_uniform_color([1.0, 0.4, 0.0])  # orange
    sphere_list.append(sphere)

# ----------------------
# NEUE Visualisierung: Grün + Grau + Kugeln
# ----------------------
print("📗 Erzeuge alternative Visualisierung mit einheitlichem Grün/Grau ...")

# Punktwolke aufteilen
noise_points = vegetation[labels == -1]
tree_points = vegetation[labels != -1]

# Punktwolke: Noise = grau
pcd_noise = o3d.geometry.PointCloud()
pcd_noise.points = o3d.utility.Vector3dVector(noise_points)
pcd_noise.paint_uniform_color([0.5, 0.5, 0.5])  # grau

# Punktwolke: restliche Vegetation = grün
pcd_green = o3d.geometry.PointCloud()
pcd_green.points = o3d.utility.Vector3dVector(tree_points)
pcd_green.paint_uniform_color([0.6, 1.0, 0.6])  # hellgrün

# Visualisierung
vis2 = o3d.visualization.Visualizer()
vis2.create_window(visible=True)
vis2.add_geometry(pcd_noise)
vis2.add_geometry(pcd_green)
for s in sphere_list:
    vis2.add_geometry(s)

vis2.poll_events()
vis2.update_renderer()

# Screenshot speichern
screenshot_path_2 = os.path.join(output_dir, f"baumcluster_GRUENGRAU_ID_{RunId}.png")
vis2.capture_screen_image(screenshot_path_2)
print(f" ✅ Screenshot (grün/grau) gespeichert: {screenshot_path_2}")

vis2.run()
vis2.destroy_window()
# ----------------------
# 5. Screenshot speichern
# ----------------------
print("📷 Speichere Screenshot ...")
vis = o3d.visualization.Visualizer()
vis.create_window(visible=True)
vis.add_geometry(pcd)
for s in sphere_list:
    vis.add_geometry(s)
vis.poll_events()
vis.update_renderer()

screenshot_path = os.path.join(output_dir, f"baumcluster_screenshot_ID_{RunId}.png")
vis.capture_screen_image(screenshot_path)
print(f" Screenshot gespeichert: {screenshot_path}")

# Optional: interaktive Anzeige
vis.run()
vis.destroy_window()

# print("Lade Visualisierung mit o3d ...")
# o3d.visualization.draw_geometries([pcd] + sphere_list)


# ----------------------
# 6. Laufzeit anzeigen
# ----------------------
end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = elapsed % 60
print(f"\nGesamtlaufzeit: {minutes} Minuten, {seconds:.2f} Sekunden")
