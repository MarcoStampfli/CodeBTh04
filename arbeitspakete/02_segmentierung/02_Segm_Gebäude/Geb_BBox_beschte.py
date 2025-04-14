# 📌 Komplettes Script mit PCA-ausgerichteten OBBs (XY-planar)

import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import open3d as o3d

from sklearn.cluster import KMeans, DBSCAN
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.decomposition import PCA
import networkx as nx
from shapely.geometry import Polygon

# === Parameter ===
input_path = r"arbeitspakete\02_segmentierung\02_Segm_Gebäude\input\P3A1_Gebaeude.txt"
num_kmeans_clusters = 150 # Anz Clusters fèr BBox
num_reclump_clusters = 30
code = "XY"

# === Hilfsfunktion: PCA-ausgerichtete OBB ===
def get_pca_aligned_obb(points_np):
    if len(points_np) < 3:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points_np)
        return pcd.get_axis_aligned_bounding_box()

    xy = points_np[:, :2]
    z_min = points_np[:, 2].min()
    z_max = points_np[:, 2].max()

    pca = PCA(n_components=2)
    pca.fit(xy)
    rotated = pca.transform(xy)

    min_xy = rotated.min(axis=0)
    max_xy = rotated.max(axis=0)
    center_xy = (min_xy + max_xy) / 2
    size_xy = max_xy - min_xy

    box_height = z_max - z_min
    center_z = (z_min + z_max) / 2

    center_world = pca.inverse_transform(center_xy)
    obb_center = np.array([center_world[0], center_world[1], center_z])

    R = np.eye(3)
    R[:2, :2] = pca.components_
    extent = np.array([size_xy[0], size_xy[1], box_height])

    obb = o3d.geometry.OrientedBoundingBox(obb_center, R, extent)
    return obb

# === Daten einlesen ===
df = pd.read_csv(input_path, delimiter=";", decimal=".", header=None)
df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red color (0-1)", "Green color (0-1)", "Blue color (0-1)",
              "X scan dir", "Y scan dir", "Z scan dir"]

# === KMeans Clustering ===
print("Starte KMeans-Vorsegmentierung...")
kmeans = KMeans(n_clusters=num_kmeans_clusters, random_state=42, n_init=10)
df["Color Cluster"] = kmeans.fit_predict(df[["X coordinate", "Y coordinate", "Z coordinate", "Z scan dir"]])

# === OBB-Berechnung ===
cluster_ids = sorted(df["Color Cluster"].unique())
cluster_features = []
cluster_obb = {}
for cid in cluster_ids:
    points_np = df[df["Color Cluster"] == cid][["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    centroid = points_np.mean(axis=0)
    cluster_features.append(centroid)
    obb = get_pca_aligned_obb(points_np)
    cluster_obb[cid] = obb
cluster_features = np.array(cluster_features)

# === Reclumping via 2D-Intersection (Shapely) ===
def obb_intersects(obb1, obb2):
    try:
        poly1 = np.array(obb1.get_box_points())[:, :2]
        poly2 = np.array(obb2.get_box_points())[:, :2]
        return Polygon(poly1).intersects(Polygon(poly2))
    except:
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

df["Reclump_Adjazenz"] = df["Color Cluster"].map(reclump_labels_graph).fillna(-1).astype(int)

# === Visualisierung ===
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
    pcd.paint_uniform_color([0.3, 0.3, 0.3])
    geometries.append(pcd)

    print("Zeige farbige OBB-Visualisierung nach Reclump_Adjazenz")
    o3d.visualization.draw_geometries(geometries, window_name="PCA-OBB Cluster")

# === Aufruf ===
show_obb_boxes_colored(df, cluster_obb, reclump_labels_graph)
