import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d
from scipy import ndimage as ndi
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy.ndimage import center_of_mass
from tqdm import tqdm
import open3d as o3d
# from open3d import SetViewPoint

# -------------------------------------------
# Startzeit zur Laufzeitmessung
# -------------------------------------------
start_time = time.time()

# -------------------------------------------
# Parameterdefinition (Tuningmöglichkeiten)
# -------------------------------------------
res = 0.5              # [m] CHM Rasterauflösung
min_distance = 3    # [Pixel] Abstand lokaler Maxima (Zusammenfassen der Maximas auf einem Baum)
sigma = 1            # Glättung (Gauss-Filter)
min_height = 2      # Mindesthöhe für Punkte
eps = 2              # DBSCAN: Radius
min_samples = 200       # DBSCAN: Mindestpunkte pro Cluster
diameter_min = 2.5     # [m] minimaler Kronendurchmesser
diameter_max = 11   # [m] maximaler Kronendurchmesser
# -------------------------------------------
RunID = 3
# ----------------------
# 0. Output-Ordner
# ----------------------
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\output"
os.makedirs(output_dir, exist_ok=True)
print(f"Output-Ordner: {output_dir}")

# ----------------------
# 1. Punktwolke laden (TXT)
# ----------------------
print("Lade Punktwolke ...")
txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\PW_Baeume_o_Boden.txt"
df_txt = pd.read_csv(txt_path, delimiter= ";", decimal= ".", header=None)
df_txt.columns = ['X', 'Y', 'Z']
points = df_txt[['X', 'Y', 'Z']].values

# ----------------------
# 2. Vorfilterung & Clustering
# ----------------------
print("Führe DBSCAN-Clustering durch ...")
veg_points = points[points[:, 2] > min_height]

db = DBSCAN(eps=eps, min_samples=min_samples)
labels = db.fit_predict(veg_points[:, :2])

filtered_clusters = []
for label in np.unique(labels):
    if label == -1:
        continue
    cluster = veg_points[labels == label]
    if len(cluster) < 5:
        continue
    try:
        hull = ConvexHull(cluster[:, :2])
        area = hull.area
        diameter = np.sqrt(4 * area / np.pi)
        if diameter_min <= diameter <= diameter_max:
            filtered_clusters.append(cluster)
    except:
        continue

if not filtered_clusters:
    raise ValueError("Keine gültigen Cluster gefunden!")

filtered_points = np.vstack(filtered_clusters)
print(f"Punkte nach Durchmesserfilter: {filtered_points.shape[0]}")

# ----------------------
# 3. CHM erstellen
# ----------------------
print("Erzeuge Canopy Height Model (CHM) ...")
x_min, x_max = filtered_points[:, 1].min(), filtered_points[:, 1].max()
y_min, y_max = filtered_points[:, 0].min(), filtered_points[:, 0].max()
x_bins = int(np.ceil((x_max - x_min) / res))
y_bins = int(np.ceil((y_max - y_min) / res))

# ACHTUNG: Bins [y, x] Reihenfolge wichtig
chm_stat, _, _, _ = binned_statistic_2d(
    filtered_points[:, 0], filtered_points[:, 1], filtered_points[:, 2],
    statistic='max', bins=[y_bins, x_bins]
)
chm = np.nan_to_num(chm_stat, nan=0)

# ----------------------
# 4. Lokale Maxima
# ----------------------
print("Suche Baumgipfel ...")
chm_smooth = ndi.gaussian_filter(chm, sigma=sigma)
local_max = peak_local_max(chm_smooth, min_distance=int(min_distance), labels=chm > 0)

valid = chm[local_max[:, 0], local_max[:, 1]] > 3
local_max = local_max[valid]
print(f"Lokale Maxima (gefiltert): {len(local_max)}")

# ----------------------
# 5. Watershed-Segmentierung
# ----------------------
print("Starte Watershed ...")
markers = np.zeros_like(chm, dtype=int)
for i, coord in enumerate(local_max):
    markers[coord[0], coord[1]] = i + 1

elevation = -chm_smooth
labels = watershed(elevation, markers, mask=chm > 0)
print(f"Segmente gefunden: {labels.max()}")

# ----------------------
# 6. Baumdaten extrahieren
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
    # # Schritt 1: Spiegelung an X
    # y_spiegel = y_max - cy * res

    # # Schritt 2: 
    # y = y_spiegel                  
    # x = x_min + cx * res 
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
csv_path = os.path.join(output_dir, f"baumdaten_watershed_RunID_{RunID}.csv")
df.to_csv(csv_path, index=False)
print(f"CSV gespeichert: {csv_path}")

# ----------------------
# 7. CHM Visualisierung
# ----------------------
print("Visualisiere CHM + Baumgipfel ...")
plt.figure(figsize=(10, 8))
plt.imshow(chm, cmap='viridis', origin='lower',
           extent=[x_min, x_max, y_min, y_max])

# Neue Koordinatenberechnung – passend zur Extraktion (Spiegelung + Drehung)
x_coords = y_max - local_max[:, 0] * res  # Zeile → Y → gespiegelt → X
y_coords = x_min + local_max[:, 1] * res  # Spalte → X → zu Y

plt.scatter(x_coords, y_coords, c='red', s=10, label="Baumgipfel")
plt.title("CHM mit Baumgipfeln (angepasst)")
plt.colorbar(label='Höhe [m]')
plt.legend()
fig_path = os.path.join(output_dir, f"chm_baumgipfel_RunID_{RunID}.png")
plt.savefig(fig_path, dpi=300)
print(f"CHM gespeichert: {fig_path}")
# ----------------------
# 9. Laufzeit anzeigen
# ----------------------
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")

plt.show()


# ----------------------
# 8. Open3D-Visualisierung
# ----------------------

print("Starte 3D-Visualisierung ...")
filtered_points_trans = np.copy(filtered_points)
filtered_points_trans[:, 0] = y_max - filtered_points[:, 1]  # neue X
filtered_points_trans[:, 1] = x_min + filtered_points[:, 0]  # neue Y

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(filtered_points_trans)
colors = np.tile([0.2, 0.6, 0.2], (len(filtered_points_trans), 1))
pcd.colors = o3d.utility.Vector3dVector(colors)

sphere_list = []
for _, row in df.iterrows():
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=3)
    sphere.translate([row["X"], row["Y"], row["Height_m"]])
    sphere.paint_uniform_color([1, 0.4, 0])  # orange
    sphere_list.append(sphere)

o3d.visualization.draw_geometries([pcd] + sphere_list, window_name="3D: Bäume + Zentren")