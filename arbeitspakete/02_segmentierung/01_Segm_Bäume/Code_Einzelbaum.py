import laspy
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
import open3d as o3d
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# --- 1. Punktwolke laden ---
las = laspy.read(r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\PW_Baeume_o_Boden.las")  # oder .laz
points = np.vstack((las.x, las.y, las.z)).T

# Optional: Filterung unterhalb 2 m (nur Baumkronen)
vegetation = points[points[:, 2] > 2.0]

# --- 2. DBSCAN-Clustering ---
db = DBSCAN(eps=1.5, min_samples=300) # eps= Abstand
labels = db.fit_predict(vegetation)
vegetation_with_labels = np.hstack((vegetation, labels[:, np.newaxis]))

# --- 3. Clusteranalyse ---
tree_data = []
unique_labels = np.unique(labels)
n_clusters = len(unique_labels[unique_labels != -1])

for label in unique_labels:
    if label == -1:
        continue  # Noise ignorieren
    cluster_points = vegetation_with_labels[vegetation_with_labels[:, 3] == label][:, :3]
    
    z_min = np.min(cluster_points[:, 2])
    z_max = np.max(cluster_points[:, 2])
    height = z_max - z_min
    
    hull = ConvexHull(cluster_points[:, :2])
    area = hull.area
    diameter = np.sqrt(4 * area / np.pi)
    
    centroid = np.mean(cluster_points, axis=0)
    
    tree_data.append({
        "Tree_ID": label,
        "X": centroid[0],
        "Y": centroid[1],
        "Z": centroid[2],
        "Height_m": height,
        "Crown_Diameter_m": diameter
    })

df = pd.DataFrame(tree_data)
df.to_csv("baum_cluster.csv", index=False)

# --- 4. Visualisierung mit Open3D ---
# Farbpalette
colors = cm.get_cmap("tab20", n_clusters)

# Farben zuweisen
vis_colors = np.zeros((vegetation.shape[0], 3))
for i, label in enumerate(labels):
    if label == -1:
        vis_colors[i] = [0.5, 0.5, 0.5]  # Grau für Noise
    else:
        vis_colors[i] = colors(label % 20)[:3]

# Open3D PointCloud erstellen
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(vegetation)
pcd.colors = o3d.utility.Vector3dVector(vis_colors)

# Visualisierung starten
o3d.visualization.draw_geometries([pcd], window_name="Baumcluster (DBSCAN)")
