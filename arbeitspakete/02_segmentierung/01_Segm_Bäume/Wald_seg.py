import os
import laspy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy.ndimage import center_of_mass
from tqdm import tqdm
import open3d as o3d

# ----------------------
# 0. Output-Ordner vorbereiten
# ----------------------
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
print(f"Output-Ordner: {output_dir}")

# ----------------------
# 1. Punktwolke laden
# ----------------------
print("Lade Punktwolke ...")
las = laspy.read("deine_punktwolke.las")  # <-- Datei hier anpassen
points = np.vstack((las.x, las.y, las.z)).T
points = points[points[:, 2] > 2.0]
print(f"Anzahl Punkte nach Filter (>2 m): {points.shape[0]}")

# ----------------------
# 2. CHM erstellen
# ----------------------
print("Erzeuge Canopy Height Model (CHM) ...")
res = 0.25
x_min, x_max = points[:, 0].min(), points[:, 0].max()
y_min, y_max = points[:, 1].min(), points[:, 1].max()
x_bins = int(np.ceil((x_max - x_min) / res))
y_bins = int(np.ceil((y_max - y_min) / res))

chm_stat, _, _, _ = binned_statistic_2d(
    points[:, 0], points[:, 1], points[:, 2],
    statistic='max',
    bins=[x_bins, y_bins]
)
chm = np.nan_to_num(chm_stat, nan=0)
print(f"CHM erstellt ({x_bins} x {y_bins} Zellen, Auflösung {res} m)")

# ----------------------
# 3. Lokale Maxima
# ----------------------
print("Suche lokale Maxima ...")
chm_smooth = ndi.gaussian_filter(chm, sigma=1)
local_max = peak_local_max(chm_smooth, min_distance=2, labels=chm > 0)
print(f"Gefundene Baumgipfel: {len(local_max)}")

# ----------------------
# 4. Watershed
# ----------------------
print("Starte Watershed-Segmentierung ...")
markers = np.zeros_like(chm, dtype=int)
for i, coord in enumerate(local_max):
    markers[coord[0], coord[1]] = i + 1

elevation = -chm_smooth
labels = watershed(elevation, markers, mask=chm > 0)
print(f"Segmentierte Baumregionen: {labels.max()}")

# ----------------------
# 5. Baumdaten extrahieren
# ----------------------
print("Extrahiere Baumdaten ...")
tree_data = []

for region_label in tqdm(np.unique(labels), desc="Analysiere Bäume"):
    if region_label == 0:
        continue
    mask = labels == region_label
    if np.sum(mask) < 3:
        continue

    z_vals = chm[mask]
    height = z_vals.max()
    crown_area = np.sum(mask) * res * res
    crown_diameter = np.sqrt(4 * crown_area / np.pi)

    cy, cx = center_of_mass(mask)
    x = x_min + cx * res
    y = y_min + cy * res

    tree_data.append({
        "Tree_ID": region_label,
        "X": x,
        "Y": y,
        "Height_m": round(height, 2),
        "Crown_Diameter_m": round(crown_diameter, 2)
    })

df = pd.DataFrame(tree_data)
csv_path = os.path.join(output_dir, "baumdaten_watershed.csv")
df.to_csv(csv_path, index=False)
print(f"Baumdaten gespeichert in: {csv_path} ({len(df)} Bäume)")

# ----------------------
# 6. 2D-Visualisierung speichern
# ----------------------
print("Erzeuge 2D-Visualisierung (CHM + Baumgipfel) ...")
plt.figure(figsize=(10, 8))
plt.imshow(chm, cmap='terrain', origin='lower')
plt.scatter(local_max[:, 1], local_max[:, 0], c='red', s=10, label="Baumgipfel")
plt.title("Canopy Height Model mit Baumgipfeln")
plt.colorbar(label='Höhe [m]')
plt.legend()
fig_path = os.path.join(output_dir, "chm_baumgipfel.png")
plt.savefig(fig_path, dpi=300)
plt.show()
print(f"Visualisierung gespeichert in: {fig_path}")

# ----------------------
# 7. Open3D-Visualisierung
# ----------------------
print("Starte Open3D-Visualisierung ...")
# Punktwolke
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
colors = np.tile([0.3, 0.6, 0.3], (len(points), 1))  # grünliche Punkte
pcd.colors = o3d.utility.Vector3dVector(colors)

# Kugeln für Baumzentren
sphere_list = []
for _, row in df.iterrows():
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.5)
    sphere.translate([row["X"], row["Y"], row["Height_m"]])
    sphere.paint_uniform_color([1, 0, 0])  # rot
    sphere_list.append(sphere)

o3d.visualization.draw_geometries([pcd] + sphere_list, window_name="Baumzentren (Watershed)")
