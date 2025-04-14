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
import networkx as nx
from shapely.geometry import Polygon

# === Parameter ===
input_path = r"arbeitspakete\02_segmentierung\02_Segm_Gebäude\input\P3A1_Gebaeude.txt"
num_kmeans_clusters = 100
num_reclump_clusters = 15
delta_aabb = 2.0  # Toleranz für BoundingBox-Adjazenz (Meter)
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
cluster_obb = {}
for cid in cluster_ids:
    points_np = df[df["Color Cluster"] == cid][["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    centroid = points_np.mean(axis=0)
    cluster_features.append(centroid)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points_np)
    obb = pcd.get_oriented_bounding_box()
    cluster_obb[cid] = obb
cluster_features = np.array(cluster_features)

# === Schritt 4A: Reclumping mit KMeans ===
reclump_kmeans = KMeans(n_clusters=num_reclump_clusters, random_state=42, n_init=10)
kmeans_labels = reclump_kmeans.fit_predict(cluster_features)
df["Reclump_KMeans"] = df["Color Cluster"].map(dict(zip(cluster_ids, kmeans_labels)))

# === Schritt 4B: Reclumping mit DBSCAN ===
dbscan = DBSCAN(eps=10, min_samples=2)
dbscan_labels = dbscan.fit_predict(cluster_features)
df["Reclump_DBSCAN"] = df["Color Cluster"].map(dict(zip(cluster_ids, dbscan_labels)))

# === Schritt 4C: Reclumping mit Hierarchischem Clustering ===
linkage_matrix = linkage(cluster_features, method="ward")
hier_labels = fcluster(linkage_matrix, t=num_reclump_clusters, criterion='maxclust')
df["Reclump_Hierarchisch"] = df["Color Cluster"].map(dict(zip(cluster_ids, hier_labels)))

# === Schritt 4D: Reclumping basierend auf OBB-Intersection ===
def obb_intersects(obb1, obb2):
    # 2D-Intersection durch Projektion auf XY-Ebene
    poly1 = np.array(obb1.get_box_points())[:, :2]
    poly2 = np.array(obb2.get_box_points())[:, :2]

    
    try:
        intersection = Polygon(poly1).intersection(Polygon(poly2))
        return intersection.area > 0
    except Exception as e:
        print(f"Intersection Error: {e}")
        return False

G = nx.Graph()
for i, cid1 in enumerate(cluster_ids):
    obb1 = cluster_obb[cid1]
    for j in range(i + 1, len(cluster_ids)):
        cid2 = cluster_ids[j]
        obb2 = cluster_obb[cid2]
        if obb_intersects(obb1, obb2):
            G.add_edge(cid1, cid2)

components = list(nx.connected_components(G))
reclump_labels_graph = {}
for label, comp in enumerate(components):
    for cid in comp:
        reclump_labels_graph[cid] = label

df["Reclump_Adjazenz"] = df["Color Cluster"].map(reclump_labels_graph)
df["Reclump_Adjazenz"] = df["Reclump_Adjazenz"].fillna(-1).astype(int)

# === Schritt 5: Visualisierung ===
def show_open3d_cluster(df, cluster_column, title):
    points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    labels = df[cluster_column].to_numpy()

    if np.all(labels == labels[0]):
        print(f"Nur ein einziger Cluster in '{cluster_column}': {labels[0]}")
        norm_labels = np.zeros_like(labels)
    else:
        norm_labels = (labels - labels.min()) / (labels.max() - labels.min() + 1e-5)

    colors = plt.cm.jet(norm_labels)[:, :3]
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    print(f"Zeige Visualisierung für: {title}")
    o3d.visualization.draw_geometries([pcd], window_name=title)

# === OBB-Visualisierung mit Farben pro Reclump_Adjazenz ===
def show_obb_boxes_colored(df, cluster_obb, reclump_labels):
    geometries = []
    cmap = plt.get_cmap("tab20")
    max_label = max(reclump_labels.values()) if reclump_labels else 1

    for cid, obb in cluster_obb.items():
        label = reclump_labels.get(cid, -1)
        color = cmap(label / max_label)[:3] if label >= 0 else (0.5, 0.5, 0.5)
        obb.color = color
        geometries.append(obb)

    points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.paint_uniform_color([0.2, 0.2, 0.2])
    geometries.append(pcd)

    print("Zeige farbige OBB-Visualisierung nach Reclump_Adjazenz")
    o3d.visualization.draw_geometries(geometries, window_name="Farbige OBB der Cluster")

# Visualisierung der vier Methoden
# show_open3d_cluster(df, "Reclump_KMeans", "Reclumping mit KMeans")
# show_open3d_cluster(df, "Reclump_DBSCAN", "Reclumping mit DBSCAN")
# show_open3d_cluster(df, "Reclump_Hierarchisch", "Reclumping mit Hierarchischem Clustering")
show_open3d_cluster(df, "Reclump_Adjazenz", "Reclumping mit BoundingBox Adjazenz")

# Farbige OBB-Visualisierung
show_obb_boxes_colored(df, cluster_obb, reclump_labels_graph)
