import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os

# ==== 1. Dateipfade eintragen ====
csv_files = [
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten1.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten2.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten3.csv",
]


# Output Ordner
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)

# ==== 2. CSVs einlesen und in eine Liste von DataFrames speichern ====
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    # Umbenennen, damit die Spalten gleich sind
    df = df.rename(columns={"E": "X", "N": "Y", "Height_m": "Z"})
    # Falls weitere Spalten vorhanden, ggf. entfernen
    df = df[["Tree_ID", "X", "Y", "Z", "Crown_Diameter_m"]]
    dfs.append(df)

# ==== 3. Alle DataFrames zu einem DataFrame stapeln ====
all_trees = pd.concat(dfs, ignore_index=True)

# ==== 4. Duplikate finden und entfernen ====
# Definiere einen Toleranzwert für "Gleiche Bäume" in Metern
TOLERANZ = 1.0  # Meter, nach Bedarf anpassen

# Sortiere nach X, Y (optional, für schnelleren Vergleich)
all_trees = all_trees.sort_values(by=["X", "Y"]).reset_index(drop=True)

# Nutze KDTree, um Duplikate zu finden
coords = all_trees[["X", "Y"]].values
tree = cKDTree(coords)
# Finde alle Nachbarn im Toleranzradius (einschließlich sich selbst)
matches = tree.query_ball_tree(tree, r=TOLERANZ)

# Erzeuge eine Maske, um nur das "erste Vorkommen" jedes Duplikats zu behalten
mask = np.ones(len(all_trees), dtype=bool)
for i, neighbors in enumerate(matches):
    # Behalte nur den ersten (niedrigsten Index)
    if not mask[i]:
        continue
    for j in neighbors:
        if j > i:
            mask[j] = False

unique_trees = all_trees[mask].reset_index(drop=True)
unique_trees["Tree_ID"] = unique_trees.index  # Neue IDs ab 0

# ==== 5. Ausgabe speichern ====
output_path = os.path.join(output_dir, f"baumdaten_watershed_merged.csv")
unique_trees.to_csv(output_path, index=False)

print(f"Erfolgreich zusammengeführt! Anzahl Bäume: {len(unique_trees)}")
print(f"Datei gespeichert unter: {output_path}")
