import os
import time
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

# -------------------------------------------
# Startzeit zur Laufzeitmessung
# -------------------------------------------
start_time = time.time()

# -------------------------------------------
# Parameterdefinition (Tuningmöglichkeiten)
# -------------------------------------------
res = 0.5            # [m] Rasterauflösung des CHM (=Zeitintensiv bei kleiner Aufl.!!!)
min_distance = 5     # [Pixel] Mindestabstand für lokale Maxima
sigma = 1.5          # [optional] Glättung des CHM (Gauss-Filter)
# -------------------------------------------

# ----------------------
# 0. Output-Ordner
# ----------------------
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\output"
os.makedirs(output_dir, exist_ok=True)
print(f"Output-Ordner: {output_dir}")

# ----------------------
# 1. Punktwolke laden
# ----------------------
print("Lade Punktwolke ...")
las = laspy.read(r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\PW_Baeume_o_Boden.las")  # <-- Datei hier anpassen
points = np.vstack((las.x, las.y, las.z)).T
points = points[points[:, 2] > 2.0]
print(f"Punkte nach Filter (>2 m): {points.shape[0]}")

# ----------------------
# 2. CHM erstellen
# ----------------------
print("Erzeuge Canopy Height Model (CHM) ...")
x_min, x_max = points[:, 0].min(), points[:, 0].max()
y_min, y_max = points[:, 1].min(), points[:, 1].max()
x_bins = int(np.ceil((x_max - x_min) / res))
y_bins = int(np.ceil((y_max - y_min) / res))

chm_stat, _, _, _ = binned_statistic_2d(
    points[:, 0],  # X
    points[:, 1],  # Y
    points[:, 2],  # Z
    statistic='max',
    bins=[x_bins, y_bins]
)

chm = np.nan_to_num(chm_stat, nan=0)
print(f"CHM: {x_bins} x {y_bins} Zellen, Auflösung {res} m")

# ----------------------
# 3. Lokale Maxima
# ----------------------
print("Finde Baumgipfel ...")
chm_smooth = ndi.gaussian_filter(chm, sigma=sigma)
local_max = peak_local_max(chm_smooth, min_distance=min_distance, labels=chm > 0)
print(f"Lokale Maxima: {len(local_max)}")

# ----------------------
# 4. Watershed
# ----------------------
print("Segmentiere Kronen mit Watershed ...")
markers = np.zeros_like(chm, dtype=int)
for i, coord in enumerate(local_max):
    markers[coord[0], coord[1]] = i + 1

elevation = -chm_smooth
labels = watershed(elevation, markers, mask=chm > 0)
print(f"Baumsegmente erkannt: {labels.max()}")

# ----------------------
# 5. Baumdaten extrahieren
# ----------------------
print("Extrahiere Baumdaten ...")
tree_data = []

for region_label in tqdm(np.unique(labels), desc="Bäume analysieren"):
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
    y = y_min + cy * res
    x = x_min + cx * res

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
print(f"CSV gespeichert: {csv_path} ({len(df)} Bäume)")

# ----------------------
# 6. Visualisierung speichern
# ----------------------
print("Erzeuge CHM-Visualisierung ...")
plt.figure(figsize=(10, 8))
# plt.imshow(chm, cmap='terrain', origin='lower',
#            extent=[x_min, x_max, y_min, y_max])
plt.imshow(chm, cmap='viridis', origin='lower',
           extent=[x_min, x_max, y_min, y_max])


# ACHTUNG: local_max ist in [Zeile, Spalte] = [Y, X]
y_coords = y_min + local_max[:, 0] * res  # Zeile → Y
x_coords = x_min + local_max[:, 1] * res  # Spalte → X

plt.scatter(x_coords, y_coords, c='red', s=10, label="Baumgipfel")

plt.title("CHM mit Baumgipfeln")
plt.colorbar(label='Höhe [m]')
plt.legend()
fig_path = os.path.join(output_dir, "chm_baumgipfel.png")
plt.savefig(fig_path, dpi=300)

# Laufzeit berechnen und ausgeben
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")

plt.show()
print(f"CHM-Visualisierung gespeichert: {fig_path}")

# ----------------------
# 7. Open3D-Visualisierung
# ----------------------
print("Starte Open3D-Visualisierung ...")
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
colors = np.tile([0.3, 0.6, 0.3], (len(points), 1))  # grün
pcd.colors = o3d.utility.Vector3dVector(colors)

sphere_list = []
for _, row in df.iterrows():
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.5)
    sphere.translate([row["X"], row["Y"], row["Height_m"]])
    sphere.paint_uniform_color([1, 0, 0])  # rot
    sphere_list.append(sphere)

o3d.visualization.draw_geometries([pcd] + sphere_list, window_name="Baumzentren (Watershed)")
