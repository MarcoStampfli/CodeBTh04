import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
import open3d as o3d
import matplotlib.cm as cm
import time

datei = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\2097_Export_PW_Ellipsenfit_normalisiert.txt"
start = time.time()

# Parameter
klass = 2           # Klassen KMeans
eps = 0.7           # eps 0.5–1.0 (je nach Punktdichte, Baumabstand)
min_samples = 50    # Min Punkte für Cluster

# Punktwolke laden
df = pd.read_csv(datei, delimiter=";", decimal=".", header=None)

df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red (0-1)", "Green (0-1)", "Blue (0-1)",
              "Hue_norm", "Saturation_norm", "Value_norm",
              "X scan dir", "Y scan dir", "Z scan dir"]

# 2. RGB-KMeans (2 Cluster: Grün vs. Nicht-Grün)
rgb = df[["Red (0-1)", "Green (0-1)", "Blue (0-1)"]].to_numpy()
kmeans = KMeans(n_clusters=klass, random_state=0).fit(rgb)
df["kmeans_label"] = kmeans.labels_

# 3. Grünsten Cluster ermitteln
green_cluster = df.groupby("kmeans_label")["Green (0-1)"].mean().idxmax()
df["is_green"] = (df["kmeans_label"] == green_cluster).astype(int)

endKM= time.time()
duration = endKM - start
print(f"-> KMeans abgeschlossen in {duration:.2f} Sekunden")

# 4. DBSCAN auf grünen Punkten (X/Y)
green_df = df[df["is_green"] == 0].copy()
xy = green_df[["X coordinate", "Y coordinate"]].to_numpy()
db = DBSCAN(eps=eps, min_samples=min_samples).fit(xy)
green_df["cluster_id"] = db.labels_

#  🔍 Noise-Punkte extrahieren (nicht geclusterte grüne Punkte)
noise_df = green_df[green_df["cluster_id"] == -1].copy()
print(f"Anzahl Noise-Punkte: {len(noise_df)}")

# Visualisiere Noise-Punkte in Gelb
pc_noise = o3d.geometry.PointCloud()
pc_noise.points = o3d.utility.Vector3dVector(noise_df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
pc_noise.paint_uniform_color([1.0, 1.0, 0.0])  # Gelb

# 5. Farben je Cluster (Open3D)
unique_labels = green_df["cluster_id"].unique()
colors = cm.get_cmap("tab20", len(unique_labels))
cluster_colors = {label: colors(i % 20)[:3] for i, label in enumerate(unique_labels)}

green_df["color_r"] = green_df["cluster_id"].map(lambda l: cluster_colors[l][0])
green_df["color_g"] = green_df["cluster_id"].map(lambda l: cluster_colors[l][1])
green_df["color_b"] = green_df["cluster_id"].map(lambda l: cluster_colors[l][2])

pc_clustered = o3d.geometry.PointCloud()
pc_clustered.points = o3d.utility.Vector3dVector(green_df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
pc_clustered.colors = o3d.utility.Vector3dVector(green_df[["color_r", "color_g", "color_b"]].to_numpy())

# Bestehende Visualisierung erweitern
o3d.visualization.draw_geometries([pc_clustered, pc_noise])

# 6. Circle Fit + Durchmesserfilter
def fit_circle_2d(x, y):
    A = np.c_[2*x, 2*y, np.ones_like(x)]
    b = x**2 + y**2
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    xc, yc = c[0], c[1]
    r = np.sqrt(c[2] + xc**2 + yc**2)
    return xc, yc, r

diameter_min = 2.5
diameter_max = 11

valid_centroids = []
valid_radii = []

for label in unique_labels:
    if label == -1:
        continue
    cluster_pts = green_df[green_df["cluster_id"] == label]
    x = cluster_pts["X coordinate"].to_numpy()
    y = cluster_pts["Y coordinate"].to_numpy()

    if len(x) < 10:
        continue

    xc, yc, r = fit_circle_2d(x, y)
    diameter = 2 * r

    if diameter_min <= diameter <= diameter_max:
        zc = cluster_pts["Z coordinate"].mean()
        valid_centroids.append([xc, yc, zc])
        valid_radii.append(r)

DBscan= time.time()
duration = DBscan - endKM
print(f"-> DBScan abgeschlossen in {duration:.2f} Sekunden")

# 7. Visualisierung der Mittelpunkte + Radien
valid_centroids = np.array(valid_centroids)

# Rote Mittelpunkte
pc_valid = o3d.geometry.PointCloud()
pc_valid.points = o3d.utility.Vector3dVector(valid_centroids)
pc_valid.paint_uniform_color([1.0, 0.0, 0.0])  # rot

# Grüne Kugeln für Baumkronen
spheres = []
for pt, radius in zip(valid_centroids, valid_radii):
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
    sphere.translate(pt)
    sphere.paint_uniform_color([0.0, 1.0, 0.0])
    spheres.append(sphere)

# 8. Visualisierung
o3d.visualization.draw_geometries([pc_clustered, *spheres])

# 9. Export als CSV
df_trees = pd.DataFrame(valid_centroids, columns=["X", "Y", "Z"])
df_trees["radius"] = valid_radii
df_trees["diameter"] = df_trees["radius"] * 2
df_trees.to_csv("baum_mittelpunkte_und_radien.csv", index=False)
