from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import open3d as o3d
import time

datei = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\2097_Export_PW_Ellipsenfit_normalisiert.txt"
start = time.time()
# Punktwolke laden
df = pd.read_csv(datei, delimiter=";", decimal=".", header=None)

df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red (0-1)", "Green (0-1)", "Blue (0-1)",
              "Hue_norm", "Saturation_norm", "Value_norm",
              "X scan dir", "Y scan dir", "Z scan dir"]


# RGB-Featurematrix
rgb = df[["Red (0-1)", "Green (0-1)", "Blue (0-1)"]].to_numpy()

# KMeans mit 2 Clustern
kmeans = KMeans(n_clusters=2, random_state=0).fit(rgb)
df["kmeans_label"] = kmeans.labels_

# Ermittele den grünsten Cluster
cluster_green_means = df.groupby("kmeans_label")["Green (0-1)"].mean()
green_cluster = cluster_green_means.idxmax()

# Binäre Klasse: 0 = grün, 1 = nicht grün
df["is_green"] = (df["kmeans_label"] == green_cluster).astype(int)

# # Punktwolken für Visualisierung (mit fester Farbe für grün)
def make_pc(points_df, uniform_color):
    pc = o3d.geometry.PointCloud()
    pc.points = o3d.utility.Vector3dVector(points_df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
    pc.paint_uniform_color(uniform_color)
    return pc

# # Farben: hellgrün für grüne Klasse, grau für alle anderen
pc_green = make_pc(df[df["is_green"] == 0], uniform_color=[0.6, 1.0, 0.6])  # hellgrün
pc_other = make_pc(df[df["is_green"] == 1], uniform_color=[0.5, 0.5, 0.5])  # grau

# # Visualisierung
# o3d.visualization.draw_geometries([pc_other, pc_green])

# Visualisierung
# o3d.visualization.draw_geometries([pc_green])

# Visualisierung
o3d.visualization.draw_geometries([pc_other])


from sklearn.cluster import DBSCAN
import matplotlib.cm as cm
import matplotlib.pyplot as plt

endKM= time.time()
duration = endKM - start
print(f"-> KMeans abgeschlossen in {duration:.2f} Sekunden")

# 1. Nur grüne Punkte für das Clustering verwenden
green_df = df[df["is_green"] == 0].copy()

# Parameter
eps = 0.7           # eps 0.5–1.0 (je nach Punktdichte, Baumabstand)
min_samples = 50   # Min Punkte für Cluster

# 2. DBSCAN auf X/Y
xy = green_df[["X coordinate", "Y coordinate"]].to_numpy()
db = DBSCAN(eps=eps, min_samples=min_samples).fit(xy)
green_df["cluster_id"] = db.labels_

# 3. Zufällige Farben je Cluster (Open3D erwartet RGB 0–1)
unique_labels = green_df["cluster_id"].unique()
n_labels = len(unique_labels)
colors = cm.get_cmap("tab20", n_labels)  # oder "nipy_spectral", "viridis", etc.

cluster_colors = {
    label: colors(i % 20)[:3]  # RGB ohne Alpha
    for i, label in enumerate(unique_labels)
}

green_df["color_r"] = green_df["cluster_id"].map(lambda l: cluster_colors[l][0])
green_df["color_g"] = green_df["cluster_id"].map(lambda l: cluster_colors[l][1])
green_df["color_b"] = green_df["cluster_id"].map(lambda l: cluster_colors[l][2])

DBscan= time.time()
duration = DBscan - endKM
print(f"-> DBScan abgeschlossen in {duration:.2f} Sekunden")

# 4. Open3D Punktwolke für Cluster
pc_clustered = o3d.geometry.PointCloud()
pc_clustered.points = o3d.utility.Vector3dVector(green_df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
pc_clustered.colors = o3d.utility.Vector3dVector(green_df[["color_r", "color_g", "color_b"]].to_numpy())

# 5. Optional: Mittelpunkte berechnen (per Mittelwert, später Circle Fit)
centroids = []
for label in unique_labels:
    if label == -1: continue  # Noise
    cluster_pts = green_df[green_df["cluster_id"] == label]
    x_mean = cluster_pts["X coordinate"].mean()
    y_mean = cluster_pts["Y coordinate"].mean()
    z_mean = cluster_pts["Z coordinate"].mean()
    centroids.append([x_mean, y_mean, z_mean])

# Mittelpunkte als Kugeln (kleine Punkte)
centroid_pcd = o3d.geometry.PointCloud()
centroid_pcd.points = o3d.utility.Vector3dVector(np.array(centroids))
centroid_pcd.paint_uniform_color([1.0, 0.0, 0.0])  # rot

# 6. Visualisierung
o3d.visualization.draw_geometries([pc_clustered, centroid_pcd])