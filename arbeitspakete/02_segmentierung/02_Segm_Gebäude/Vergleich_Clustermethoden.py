# 📌 Notebook: Reclumping von Gebäude-Segmenten aus Punktwolken

import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import time
import matplotlib.pyplot as plt
import open3d as o3d

from sklearn.cluster import KMeans, DBSCAN
from scipy.cluster.hierarchy import linkage, fcluster

# === Parameter ===
input_path = r"arbeitspakete\02_segmentierung\02_Segm_Gebäude\input\P3A1_Gebaeude.txt"
num_kmeans_clusters = 100
num_reclump_clusters = 25

# Parametters DBScan
eps=5          # Suchradius in Metern 
min_samples=2   # min. Cluster zusammen mergen

code = "XY"

# === Schritt 1: Daten einlesen ===
df = pd.read_csv(input_path, delimiter=";", decimal=".", header=None)
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-1)", "Green color (0-1)", "Blue color (0-1)", 
              "X scan dir", "Y scan dir", "Z scan dir"]

# === Schritt 2: Erste KMeans-Clustering (fein) ===
print("Starte KMeans-Vorsegmentierung...")
kmeans = KMeans(n_clusters=num_kmeans_clusters, random_state=42, n_init=10)
df["Color Cluster"] = kmeans.fit_predict(df[["X coordinate", "Y coordinate", "Z coordinate", "Z scan dir"]])

# === Schritt 3: Clusterzentren berechnen ===
cluster_ids = sorted(df["Color Cluster"].unique())
cluster_features = []
for cid in cluster_ids:
    points = df[df["Color Cluster"] == cid][["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    centroid = points.mean(axis=0)
    cluster_features.append(centroid)
cluster_features = np.array(cluster_features)

# === Schritt 4A: Reclumping mit KMeans ===
reclump_kmeans = KMeans(n_clusters=num_reclump_clusters, random_state=42, n_init=10)
kmeans_labels = reclump_kmeans.fit_predict(cluster_features)
df["Reclump_KMeans"] = df["Color Cluster"].map(dict(zip(cluster_ids, kmeans_labels)))

# === Schritt 4B: Reclumping mit DBSCAN ===
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
dbscan_labels = dbscan.fit_predict(cluster_features)
df["Reclump_DBSCAN"] = df["Color Cluster"].map(dict(zip(cluster_ids, dbscan_labels)))

# === Schritt 4C: Reclumping mit Hierarchischem Clustering ===
linkage_matrix = linkage(cluster_features, method="ward")
hier_labels = fcluster(linkage_matrix, t=num_reclump_clusters, criterion='maxclust')
df["Reclump_Hierarchisch"] = df["Color Cluster"].map(dict(zip(cluster_ids, hier_labels)))

# === Schritt 5: Visualisierung ===
def show_open3d_cluster(df, cluster_column, title):
    points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    labels = df[cluster_column].to_numpy()
    norm_labels = (labels - labels.min()) / (labels.max() + 1e-5)
    colors = plt.cm.jet(norm_labels)[:, :3]

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    
    print(f"Zeige Visualisierung für: {title}")
    o3d.visualization.draw_geometries([pcd], window_name=title)

# Visualisierung der drei Methoden
show_open3d_cluster(df, "Reclump_KMeans", "Reclumping mit KMeans")
show_open3d_cluster(df, "Reclump_DBSCAN", "Reclumping mit DBSCAN")
show_open3d_cluster(df, "Reclump_Hierarchisch", "Reclumping mit Hierarchischem Clustering")
