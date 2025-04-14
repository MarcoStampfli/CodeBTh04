import pandas as pd
import numpy as np
import os
import time
from tqdm import tqdm
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import open3d as o3d

# Startzeit
start_time = time.time()

# === Parameter ===
input_path = r"arbeitspakete\02_segmentierung\02_Segm_Gebäude\input\P3A1_Gebaeude.txt"
num_clusters = 100         # Feine KMeans-Segmente (1.Schritt)
num_reclump_clusters = 26  # Grobe Gebäude-Cluster (2. Schritt)
code = "XY"

# === Punktwolke laden ===
df = pd.read_csv(input_path, delimiter=";", decimal=".", header=None)
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-1)", "Green color (0-1)", "Blue color (0-1)", 
              "X scan dir", "Y scan dir", "Z scan dir"]

# === KMeans Clustering auf Punktbasis ===
print("Starte K-Means Clustering...")
with tqdm(total=100, desc="Clustering") as pbar:
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    df["Color Cluster"] = kmeans.fit_predict(df[["X coordinate", "Y coordinate", "Z coordinate", "Z scan dir"]])
    pbar.update(100)

# === Reclumping der Cluster (Cluster der Cluster) ===
print("Führe Reclumping durch...")
cluster_features = []
cluster_ids = sorted(df["Color Cluster"].unique())

for cluster_id in cluster_ids:
    cluster_pts = df[df["Color Cluster"] == cluster_id][["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    centroid = cluster_pts.mean(axis=0)
    cluster_features.append(centroid)

cluster_features = np.array(cluster_features)

# Zweites Clustering
reclump_kmeans = KMeans(n_clusters=num_reclump_clusters, random_state=42, n_init=10)
reclump_labels = reclump_kmeans.fit_predict(cluster_features)

# Mapping zurück auf Punktwolke
reclump_map = dict(zip(cluster_ids, reclump_labels))
df["Reclump Cluster"] = df["Color Cluster"].map(reclump_map)

# === Visualisierung ===
print("Visualisiere Punktwolke mit Reclumping-Farben...")
points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
reclump_norm = df["Reclump Cluster"].to_numpy() / (df["Reclump Cluster"].max() + 1)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(plt.cm.jet(reclump_norm)[:, :3])

o3d.visualization.draw_geometries([pcd], window_name="Reclumped Punktwolke")

# === Laufzeit ===
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Fertig! Laufzeit: {int(elapsed_time // 60)} Min {elapsed_time % 60:.2f} Sek.")
