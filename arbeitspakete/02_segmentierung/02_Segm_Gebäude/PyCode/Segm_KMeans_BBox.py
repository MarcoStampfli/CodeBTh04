# 📌 Komplettes Script mit PCA-ausgerichteten OBBs (XY-planar)

import pandas as pd
import numpy as np
import time
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
input_path = r"arbeitspakete\02_segmentierung\02_Segm_Gebäude\input\Input__PW_Klasse_13_kmeans_normalisiert.txt"
num_kmeans_clusters = 2000
# num_reclump_clusters = 15
code = "XX"

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

# === Zeitmessung und Fortschritt ===
# Laufzeiten und Parameterwerte speichern
log_lines = []
log_lines.append(f"Input-Datei: {input_path}")
log_lines.append(f"Anzahl KMeans-Cluster: {num_kmeans_clusters}")
log_lines.append(f"Code-Präfix: {code}")
start_time_total = time.time()

df = pd.read_csv(input_path, delimiter=";", decimal=".", header=None)

# === Nur rechten unteren Quadranten der Punktwolke verwenden ===
min_x, max_x = df[0].min(), df[0].max()
min_y, max_y = df[1].min(), df[1].max()

# Filter: X > Mittelwert, Y < Mittelwert => rechts unten
df = df[(df[0] > (min_x + max_x) / 2) & (df[1] < (min_y + max_y) / 2)]

df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red color (0-1)", "Green color (0-1)", "Blue color (0-1)",
              "Hue (0-1)", "Saturation (0-1)", "Value (0-1)",
              "X scan dir", "Y scan dir", "Z scan dir"]

print("[1] Lese Daten ein...")
data_read_start = time.time()
print("Starte KMeans-Vorsegmentierung...")
kmeans = KMeans(n_clusters=num_kmeans_clusters, random_state=42, n_init=10)
predict = ["X coordinate", "Y coordinate", "Z scan dir"] # Kmeans Klasseneigenschaften
df["Color Cluster"] = kmeans.fit_predict(df[predict])
log_lines.append(f"Eigenschaften KMeans-Cluster: {predict}")

duration = time.time() - data_read_start
print(f"-> Daten eingelesen in {duration:.2f} Sekunden")
log_lines.append(f"Daten einlesen: {duration:.2f} Sekunden")

print("[2] Starte KMeans-Vorsegmentierung...")
kmeans_start = time.time()
cluster_ids = sorted(df["Color Cluster"].unique())
cluster_features = []
cluster_obb = {}
for cid in tqdm(cluster_ids, desc="OBBs"):
    points_np = df[df["Color Cluster"] == cid][["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    centroid = points_np.mean(axis=0)
    cluster_features.append(centroid)
    obb = get_pca_aligned_obb(points_np)
    cluster_obb[cid] = obb

duration = time.time() - kmeans_start
print(f"-> KMeans abgeschlossen in {duration:.2f} Sekunden")
log_lines.append(f"KMeans-Clustering: {duration:.2f} Sekunden")

print("[3] Berechne OBBs mit PCA...")
obb_start = time.time()
def obb_intersects(obb1, obb2):
    try:
        poly1 = np.array(obb1.get_box_points())[:, :2]
        poly2 = np.array(obb2.get_box_points())[:, :2]
        return Polygon(poly1).intersects(Polygon(poly2))
    except:
        return False

G = nx.Graph()
for i, cid1 in enumerate(tqdm(cluster_ids, desc="Cluster Adjazenzprüfung")):
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

duration = time.time() - obb_start
print(f"-> OBB-Berechnung abgeschlossen in {duration:.2f} Sekunden")
log_lines.append(f"OBB-Berechnung: {duration:.2f} Sekunden")
cluster_features = np.array(cluster_features)

print("[4] Starte Reclumping basierend auf OBB-Überlappung...")
reclump_start = time.time()
def obb_to_lineset(obb, color=(1, 0, 0)):
    obb.color = color
    return obb

df["Reclump_Adjazenz"] = df["Color Cluster"].map(reclump_labels_graph).fillna(-1).astype(int)
duration = time.time() - reclump_start
print(f"-> Reclumping abgeschlossen in {duration:.2f} Sekunden")
log_lines.append(f"Reclumping (Adjazenzanalyse): {duration:.2f} Sekunden")

def show_obb_boxes_colored(df, cluster_obb, reclump_labels):
    geometries = []
    cmap = plt.get_cmap("tab20")
    max_label = max(reclump_labels.values()) if reclump_labels else 1

    for cid, obb in cluster_obb.items():
        label = reclump_labels.get(cid, -1)
        color = cmap(label / max_label)[:3] if label >= 0 else (0.5, 0.5, 0.5)
        line_obb = obb_to_lineset(obb, color=color)
        geometries.append(line_obb)

    points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.paint_uniform_color([0.3, 0.3, 0.3])
    geometries.append(pcd)

    print("Zeige farbige OBB-Visualisierung nach Reclump_Adjazenz")
    o3d.visualization.draw_geometries(geometries, window_name="PCA-OBB Cluster")

# === Visualisierung speichern ===
output_dir = "KMeans_BBox_output"
os.makedirs(output_dir, exist_ok=True)

# 1. Vor Clustering: Punktwolke grau
pcd_raw = o3d.geometry.PointCloud()
pcd_raw.points = o3d.utility.Vector3dVector(df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
pcd_raw.paint_uniform_color([0.5, 0.5, 0.5])
# o3d.io.write_point_cloud(os.path.join(output_dir, "01_raw_punktwolke.ply"), pcd_raw)

# 2. Farbige OBBs speichern als .ply mit Linien
geometries = []
cmap = plt.get_cmap("tab20")
max_label = max(reclump_labels_graph.values()) if reclump_labels_graph else 1
for cid, obb in cluster_obb.items():
    label = reclump_labels_graph.get(cid, -1)
    color = cmap(label / max_label)[:3] if label >= 0 else (0.5, 0.5, 0.5)
    line_obb = obb_to_lineset(obb, color=color)
    geometries.append(line_obb)

# o3d.io.write_line_sets(os.path.join(output_dir, "02_colored_OBBs.ply"), geometries)

# 3. Clustering-Resultat als eingefärbte Punktwolke
labels = df["Reclump_Adjazenz"].to_numpy()
norm_labels = (labels - labels.min()) / (labels.max() - labels.min() + 1e-5)
colors = plt.cm.jet(norm_labels)[:, :3]
pcd_clustered = o3d.geometry.PointCloud()
pcd_clustered.points = o3d.utility.Vector3dVector(df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
pcd_clustered.colors = o3d.utility.Vector3dVector(colors)
# o3d.io.write_point_cloud(os.path.join(output_dir, "03_clustered_points.ply"), pcd_clustered)

# 4. Punktwolken pro Cluster-ID speichern
# cluster_dir = os.path.join(output_dir, "cluster_csv")
# os.makedirs(cluster_dir, exist_ok=True)
# for cluster_id in sorted(df["Reclump_Adjazenz"].unique()):
#     df[df["Reclump_Adjazenz"] == cluster_id].to_csv(
#         os.path.join(cluster_dir, f"cluster_{int(cluster_id)}.csv"), sep=";", index=False, decimal=".")

# 5. Komplette Punktwolke mit Cluster-ID als Spalte "ID"
df_with_id = df.copy()
df_with_id.rename(columns={"Reclump_Adjazenz": "ID"}, inplace=True)
df_with_id.to_csv(os.path.join(output_dir, "04_punktwolke_mit_ID.csv"), sep=";", index=False, decimal=".")

# === Screenshot-Funktion ===
def take_screenshot(geometries, filename):
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)
    for g in geometries:
        vis.add_geometry(g)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(os.path.join(output_dir, filename))
    vis.destroy_window()

# === Screenshots speichern ===
# Screenshot 0: KMeans Clustering (Color Cluster)
labels_kmeans = df["Color Cluster"].to_numpy()
norm_kmeans = (labels_kmeans - labels_kmeans.min()) / (labels_kmeans.max() - labels_kmeans.min() + 1e-5)
colors_kmeans = plt.cm.jet(norm_kmeans)[:, :3]
pcd_kmeans = o3d.geometry.PointCloud()
pcd_kmeans.points = o3d.utility.Vector3dVector(df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy())
pcd_kmeans.colors = o3d.utility.Vector3dVector(colors_kmeans)
take_screenshot([pcd_kmeans], "screenshot_00_kmeans_clustering.png")
# Screenshot 1: raw point cloud
take_screenshot([pcd_raw], "screenshot_01_raw.png")

# Screenshot 2: clustered colored boxes + points
geometries = []
for cid, obb in cluster_obb.items():
    label = reclump_labels_graph.get(cid, -1)
    color = cmap(label / max_label)[:3] if label >= 0 else (0.5, 0.5, 0.5)
    line_obb = obb_to_lineset(obb, color=color)
    geometries.append(line_obb)

geometries.append(pcd_clustered)
take_screenshot(geometries, "screenshot_02_clustered.png")

print("[5] Visualisierung abgeschlossen.")
end_time_total = time.time()
duration = end_time_total - start_time_total
print(f"✅ Gesamtlaufzeit: {duration:.2f} Sekunden")
log_lines.append(f"Gesamtlaufzeit: {duration:.2f} Sekunden")

with open(os.path.join(output_dir, "laufzeit_log.txt"), "w") as f:
    f.write("".join(log_lines))

# === Anzeige im Open3D-Fenster ausgewählter Zustände ===
print("Zeige Open3D Viewer für:")
print("1. Rohpunktwolke mit Reclumped OBBs")
print("2. KMeans-Clustering-Ergebnis (farbig)")
print("3. Eingefärbte Punkte (Reclump)")

# 1. Rohpunktwolke mit farbigen OBBs
geometries_raw_plus_obb = [pcd_raw] + [obb_to_lineset(obb, color=cmap(reclump_labels_graph.get(cid, -1) / max_label)[:3]) for cid, obb in cluster_obb.items()]
o3d.visualization.draw_geometries(geometries_raw_plus_obb, window_name="01 Rohpunktwolke + OBBs")

# 2. KMeans Clustering Ergebnis (eingefärbte Punkte)
o3d.visualization.draw_geometries([pcd_kmeans], window_name="02 KMeans Cluster")

# 3. Eingefärbte Punkte nach Reclump
o3d.visualization.draw_geometries([pcd_clustered], window_name="03 Reclumped Points")
show_obb_boxes_colored(df, cluster_obb, reclump_labels_graph)
