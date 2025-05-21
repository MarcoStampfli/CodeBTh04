"""
Abstract:
Dieses Skript führt mehrere Einzelbaumlisten aus unterschiedlichen Segmentierungsläufen zusammen und bereinigt die resultierende Gesamtliste um räumliche Duplikate. 
Für jeden Baum werden die Koordinaten und Kronendurchmesser berücksichtigt. Mit Hilfe eines dynamisch aktualisierten KDTree und einem Überlappungsfaktor wird geprüft, 
ob ein neu hinzukommender Baum bereits durch einen bestehenden Eintrag ausreichend abgedeckt ist. Nur eindeutig identifizierte Bäume werden übernommen. Das bereinigte, 
zusammengeführte Ergebnis wird als CSV-Datei gespeichert und dient als Grundlage für weitere Analysen oder Modellierungsprozesse.
"""

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os

file_name = "01_v3_baumdaten_watershed_merged.csv"

# Liste der Merge Dateien
csv_files = [
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_final2\baumdaten_watershed_RunID_20250517_final2.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_final4\baumdaten_watershed_RunID_20250517_final4.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_4\baumdaten_watershed_RunID_20250517_4.csv",
]

OVERLAP_FACTOR = 0.2

# Output Ordner
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)

# Initialisierung
accepted_rows = []
coords = []
radii = []
next_id = 0
tree = None

# Funktion zur Überlappungsprüfung via KDTree
def is_duplicate_kdtree(tree, coords_array, radii_array, new_row, overlap_factor):
    if tree is None or len(coords_array) == 0:
        return False

    nx, ny = new_row["X"], new_row["Y"]
    nrad = new_row["Crown_Diameter_m"] / 2.0

    # Maximaler Suchradius (konservativ): nrad * overlap_factor
    max_radius = nrad * overlap_factor
    idxs = tree.query_ball_point([nx, ny], r=max_radius)

    for idx in idxs:
        ex_x, ex_y = coords_array[idx]
        ex_rad = radii_array[idx]
        dist = np.sqrt((ex_x - nx) ** 2 + (ex_y - ny) ** 2)
        min_rad = min(ex_rad, nrad)
        if dist < min_rad * overlap_factor:
            return True
    return False

# Hauptverarbeitung
for file in csv_files:
    df = pd.read_csv(file)
    df = df.rename(columns={"E": "X", "N": "Y", "Height_m": "Z"})
    df = df[["Tree_ID", "X", "Y", "Z", "Crown_Diameter_m"]]

    for idx, row in df.iterrows():
        if not is_duplicate_kdtree(tree, coords, radii, row, OVERLAP_FACTOR):
            row_out = row.copy()
            row_out["Tree_ID"] = next_id
            accepted_rows.append(row_out)
            coords.append((row_out["X"], row_out["Y"]))
            radii.append(row_out["Crown_Diameter_m"] / 2.0)
            next_id += 1

            # KDTree aktualisieren, aber nur in sinnvollen Intervallen
            if len(accepted_rows) % 100 == 0 or len(accepted_rows) < 100:
                tree = cKDTree(coords)

# Finalen Baum nochmal erstellen
tree = cKDTree(coords)

# DataFrame aus Ergebnissen
merged = pd.DataFrame(accepted_rows)

# Export
output_path = os.path.join(output_dir, file_name)
merged.to_csv(output_path, index=False)

print(f"Bereinigt und zusammengeführt! Anzahl Bäume: {len(merged)}")
print(f"Datei gespeichert unter: {output_path}")


