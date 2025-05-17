import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os

csv_files = [
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten1.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten2.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten3.csv",
]

input_counts = {}
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    # Quelle für Nachverfolgung
    quelle = os.path.basename(file)
    df["Quelle"] = quelle
    input_counts[quelle] = len(df)
    # Spalten anpassen
    df = df.rename(columns={"E": "X", "N": "Y", "Height_m": "Z"})
    df = df[["Tree_ID", "X", "Y", "Z", "Crown_Diameter_m", "Quelle"]]
    dfs.append(df)

all_trees = pd.concat(dfs, ignore_index=True)

# Duplikate entfernen wie vorher
TOLERANZ = 1.0
coords = all_trees[["X", "Y"]].values
tree = cKDTree(coords)
matches = tree.query_ball_tree(tree, r=TOLERANZ)
mask = np.ones(len(all_trees), dtype=bool)
for i, neighbors in enumerate(matches):
    if not mask[i]:
        continue
    for j in neighbors:
        if j > i:
            mask[j] = False

unique_trees = all_trees[mask].reset_index(drop=True)
unique_trees["Tree_ID"] = unique_trees.index

# Ausgabe
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "baumdaten_watershed_merged.csv")
unique_trees.to_csv(output_path, index=False)

print(f"Erfolgreich zusammengeführt! Anzahl Bäume: {len(unique_trees)}")
print(f"Datei gespeichert unter: {output_path}\n")

# Beitrag jeder Inputdatei zur Gesamtdatenmenge (nach Merge)
merged_counts = unique_trees["Quelle"].value_counts()

# Übersicht ausgeben:
for quelle in input_counts:
    print(f"{quelle}: Ursprünglich {input_counts[quelle]} Bäume, davon {merged_counts.get(quelle, 0)} in der Merge-Datei.")

# Optional: Anteil berechnen
total = len(unique_trees)
for quelle in input_counts:
    anteil = merged_counts.get(quelle, 0) / total * 100 if total else 0
    print(f"{quelle}: Anteil in Merge {anteil:.1f}%")
