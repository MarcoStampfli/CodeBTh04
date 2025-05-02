import open3d as o3d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# === Parameter ===
input_path = r"arbeitspakete\02_segmentierung\04_Segm_Dachformen\input\komplexe_Dachtypen_normalisiert.txt"  # <-- Anpassen!
output_dir = r"arbeitspakete\02_segmentierung\04_Segm_Dachformen\output"
# === Parameter für Regiongrowing ===
angle_threshold_deg=2.0 
distance_threshold=0.5 
min_cluster_size=30




os.makedirs(output_dir, exist_ok=True)

# === 1. Punktwolke laden ===
df = pd.read_csv(input_path, delimiter=";", decimal=".", header=None)
df.columns = ["X", "Y", "Z",
              "R", "G", "B",
              "Hue", "Sat", "Val",
              "Nx", "Ny", "Nz"]

points = df[["X", "Y", "Z"]].values
pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points))

# === 2. Normalschätzung ===
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30))
pcd.normalize_normals()

# === 3. Region Growing Segmentierung ===
def region_growing_segmentation(pcd, angle_threshold_deg=angle_threshold_deg, distance_threshold=distance_threshold, min_cluster_size=min_cluster_size):
    normals = np.asarray(pcd.normals)
    points = np.asarray(pcd.points)
    kdtree = o3d.geometry.KDTreeFlann(pcd)

    angle_threshold = np.cos(np.deg2rad(angle_threshold_deg))
    visited = np.full(len(points), False)
    labels = np.full(len(points), -1)
    current_label = 0

    for idx in range(len(points)):
        if visited[idx]:
            continue

        queue = [idx]
        visited[idx] = True
        cluster = [idx]

        while queue:
            current = queue.pop()
            _, idx_neighbors, _ = kdtree.search_radius_vector_3d(pcd.points[current], 0.2)

            for nb in idx_neighbors:
                if visited[nb]:
                    continue

                vec = points[nb] - points[current]
                distance = np.linalg.norm(vec)
                if distance > distance_threshold:
                    continue

                normal_similarity = np.dot(normals[nb], normals[current])
                if normal_similarity < angle_threshold:
                    continue

                visited[nb] = True
                queue.append(nb)
                cluster.append(nb)

        if len(cluster) >= min_cluster_size:
            for pt_idx in cluster:
                labels[pt_idx] = current_label
            current_label += 1

    return labels, current_label

labels, num_labels = region_growing_segmentation(pcd)

# === 4. Ergebnis einfärben ===
colors = plt.get_cmap("tab20")(labels / (num_labels if num_labels > 0 else 1))[:, :3]
colors[labels == -1] = [0.5, 0.5, 0.5]
pcd.colors = o3d.utility.Vector3dVector(colors)

# === 5. Speichern & Visualisieren ===
# ply_path = os.path.join(output_dir, "regiongrowing_segmented.ply")
# o3d.io.write_point_cloud(ply_path, pcd)

# Screenshot speichern
screenshot_path = os.path.join(output_dir, "regiongrowing_screenshot.png")
vis = o3d.visualization.Visualizer()
vis.create_window(visible=True)
vis.add_geometry(pcd)
vis.poll_events()
vis.update_renderer()
vis.capture_screen_image(screenshot_path)
vis.destroy_window()
