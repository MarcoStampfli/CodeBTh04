import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os

file_name = "01_v3_baumdaten_watershed_merged"
# Liste der Merge Dateien
csv_files = [
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_final2\baumdaten_watershed_RunID_20250517_final2.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_final4\baumdaten_watershed_RunID_20250517_final4.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_4\baumdaten_watershed_RunID_20250517_4.csv",
]

# Output Ordner
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)

# Hilfsfunktion: Ist der neue Baum zu nah an bestehenden Bäumen (Überlappungsregel)
def is_duplicate(existing_trees, new_tree, overlap_factor):
    # Wenn noch keine Bäume, nie Duplikat
    if existing_trees.shape[0] == 0:
        return False
    # Koordinaten
    ex_XY = existing_trees[["X", "Y"]].values
    ex_rad = existing_trees["Crown_Diameter_m"].values / 2.0
    # Neuen Baum
    nx, ny = new_tree["X"], new_tree["Y"]
    nrad = new_tree["Crown_Diameter_m"] / 2.0

    # Abstand zu allen bisherigen
    dists = np.sqrt((ex_XY[:,0] - nx)**2 + (ex_XY[:,1] - ny)**2)
    # Erlaubter Minimalabstand: (kleinerer Radius) * overlap_factor
    min_rads = np.minimum(ex_rad, nrad)
    allow_dists = min_rads * overlap_factor

    # Duplikat, wenn Abstand < erlaubte Überlappung
    return np.any(dists < allow_dists)

# Mergen mit Überlappungskriterium
merged = pd.DataFrame(columns=["Tree_ID", "X", "Y", "Z", "Crown_Diameter_m"])
next_id = 0

for file in csv_files:
    df = pd.read_csv(file)
    df = df.rename(columns={"E": "X", "N": "Y", "Height_m": "Z"})
    df = df[["Tree_ID", "X", "Y", "Z", "Crown_Diameter_m"]]
    for idx, row in df.iterrows():
        if not is_duplicate(merged, row, OVERLAP_FACTOR):
            row_out = row.copy()
            row_out["Tree_ID"] = next_id  # neue IDs vergeben
            merged = merged.append(row_out, ignore_index=True)
            next_id += 1

# Export
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, file_name)
merged.to_csv(output_path, index=False)

print(f"Bereinigt und zusammengeführt! Anzahl Bäume: {len(merged)}")
print(f"Datei gespeichert unter: {output_path}")

