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
from utils import visualize_processing_steps, verify_tree_positions, zeit
# from open3d import SetViewPoint

# -------------------------------------------
# Startzeit zur Laufzeitmessung
# -------------------------------------------
start = time.time()

# -------------------------------------------
# Parameterdefinition (Tuningmöglichkeiten)
# -------------------------------------------
res = 1           # [m] CHM Rasterauflösung
min_distance = 2    # [Pixel] Abstand lokaler Maxima (Zusammenfassen der Maximas auf einem Baum)
sigma = 0            # Glättung (Gauss-Filter)
min_height = 1      # Mindesthöhe für Punkte
eps = 0.8              # DBSCAN: Radius
min_samples = 130   # DBSCAN: Mindestpunkte pro Cluster
diameter_min = 2.5    # [m] minimaler Kronendurchmesser
diameter_max = 11   # [m] maximaler Kronendurchmesser
# -------------------------------------------
datum = "20250517_final4"
RunID = f"Parameter_res{res}_minPix{min_distance}_sig{sigma}_minH{min_height}_eps{eps}_minSam{min_samples}_DM{diameter_min}bis{diameter_max}"
# ----------------------
# 0. Output-Ordner
# ----------------------
output_dir = fr"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\{datum}"
os.makedirs(output_dir, exist_ok=True)
print(f"Output-Ordner: {output_dir}")

# ----------------------
# 1. Punktwolke laden (TXT)
# ----------------------
print("Lade Punktwolke ...")
txt_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\PW_Baeume_o_Boden_o_Rauschen.txt"
df_txt = pd.read_csv(txt_path, delimiter= ";", decimal= ".", header=None)
df_txt.columns = ['X', 'Y', 'Z']
points = df_txt[['X', 'Y', 'Z']].values
start_time = zeit(start, msg="1. Punktwolke geladen – ")
# ----------------------
# 2. Vorfilterung & Clustering
# ----------------------
print("Führe DBSCAN-Clustering durch ...")
veg_points = points[points[:, 2] > min_height]

db = DBSCAN(eps=eps, min_samples=min_samples)
labels = db.fit_predict(veg_points[:, :2])

filtered_points = []
filtered_labels = []

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
            filtered_points.append(cluster)
            filtered_labels.extend([label] * len(cluster))
    except:
        continue

if not filtered_points:
    raise ValueError("Keine gültigen Cluster gefunden!")

filtered_points = np.vstack(filtered_points)
filtered_labels = np.array(filtered_labels)

print(f"Punkte nach Durchmesserfilter: {filtered_points.shape[0]}")

start_time = zeit(start_time, msg="2. DBSCAN – ")
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
    filtered_points[:, 0], 
    filtered_points[:, 1], 
    filtered_points[:, 2],
    statistic='max', 
    bins=[y_bins, x_bins]
)
chm = np.nan_to_num(chm_stat, nan=0)
start_time = zeit(start_time, msg="3. Canopy Height Model – ")
# ----------------------
# 4. Lokale Maxima
# ----------------------
print("Suche Baumgipfel ...")
chm_smooth = ndi.gaussian_filter(chm, sigma=sigma)
local_max = peak_local_max(chm_smooth, min_distance=int(min_distance), labels=chm > 0)

valid = chm[local_max[:, 0], local_max[:, 1]] > min_height
local_max = local_max[valid]
print(f"Lokale Maxima (gefiltert): {len(local_max)}")
start_time = zeit(start_time, msg="4. Lokale Maxima – ")
# ----------------------
# 5. Watershed-Segmentierung
# ----------------------
print("Segmentiere Kronen mit Watershed ...")
markers = np.zeros_like(chm, dtype=int)
for i, coord in enumerate(local_max):
    markers[coord[0], coord[1]] = i + 1

elevation = -chm_smooth
labels = watershed(elevation, markers, mask=chm > 0)
print(f"Segmente gefunden: {labels.max()}")
start_time = zeit(start_time, msg="5. Watershed-Segmentierung – ")
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
    N = x_min + cx * res  # Nordwert
    E = y_min + cy * res  # Ostwert       

    tree_data.append({
        "Tree_ID": region_label,
        "E": E,
        "N": N,
        "Height_m": round(height, 2),
        "Crown_Diameter_m": round(crown_diameter, 2)
    })

tqdm._instances.clear()

df = pd.DataFrame(tree_data)
# # Spalten umbenennen und E/N tauschen
# df = pd.DataFrame(tree_data)
# df = df.rename(columns={"X": "E", "Y": "N"})
# df = df[["Tree_ID", "E", "N", "Height_m", "Crown_Diameter_m"]]
# Speichern
csv_path = os.path.join(output_dir, f"baumdaten_watershed_RunID_{datum}.csv")
df.to_csv(csv_path, decimal=".", columns=["Tree_ID", "E", "N", "Height_m", "Crown_Diameter_m"], index=False)
print(f"CSV gespeichert: {csv_path}")
start_time = zeit(start_time, msg="6. Baumdaten extrahieren und speichern – ")

# ----------------------
# 7. Visualisierungen erstellen
# ----------------------
# Plots zu den Arbeitsstritten erstellen
visualize_processing_steps(
    filtered_points=filtered_points,
    filtered_labels=filtered_labels,
    chm=chm,
    chm_smooth=chm_smooth,
    local_max=local_max,
    labels_ws=labels,
    output_dir=output_dir,
    df=df,
    x_min=x_min, x_max=x_max, 
    y_min=y_min, y_max=y_max, 
    res=res, RunID=RunID
    )

start_time = zeit(start_time, msg="7. Visualisierungen erstellt – ")

# ----------------------
# 9. Laufzeit anzeigen
# ----------------------
zeit(start, msg="Gesamtlaufzeit – ")

# ----------------------
# 10. PW mit gelabelten Bäumen darstellen (Matplotlib)
# ----------------------

verify_tree_positions(output_dir=output_dir, txt_path=txt_path, csv_path=csv_path)

# ----------------------
# 11. PW mit gelabelten Bäumen darstellen interaktiv (Open3D)
# ----------------------