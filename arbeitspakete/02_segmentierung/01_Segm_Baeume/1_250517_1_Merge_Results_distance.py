# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
"""
Abstract:
Dieses Skript vereinigt mehrere Listen einzelner Baumdetektionen aus verschiedenen Segmentierungsläufen zu einer bereinigten Gesamtliste. 
Die Einzeldateien werden geladen, zusammengeführt und mit Hilfe eines räumlichen Abstandsfilters (KDTree) von Duplikaten bereinigt. 
Für jeden Baum werden Koordinaten und Kronendurchmesser berücksichtigt, so dass nahe beieinanderliegende Detektionen als Duplikate erkannt und entfernt werden. 
Nach dem Merge wird ausgegeben, wie viele Bäume aus jeder Ursprungsdatei im Endergebnis enthalten sind und welcher Anteil dies jeweils ausmacht. 
Das Skript eignet sich zur konsolidierten Auswertung und Dokumentation von Einzelbaumsegmentierungen bei verschiedenen Parameterläufen oder Datenquellen.
"""

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os


# Code zum Zusammenführen der verschiedenen Ergebnisse
'''
V1 Abstand 1m
Erfolgreich zusammengeführt! Anzahl Bäume: 4244

Datei gespeichert unter: arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\baumdaten_watershed_merged.csv

baumdaten_watershed_RunID_20250517_final2.csv: Ursprünglich 3251 Bäume, davon 3251 in der Merge-Datei.
baumdaten_watershed_RunID_20250517_final4.csv: Ursprünglich 3082 Bäume, davon 611 in der Merge-Datei.
baumdaten_watershed_RunID_20250517_4.csv: Ursprünglich 3271 Bäume, davon 382 in der Merge-Datei.
baumdaten_watershed_RunID_20250517_final2.csv: Anteil in Merge 76.6%
baumdaten_watershed_RunID_20250517_final4.csv: Anteil in Merge 14.4%
baumdaten_watershed_RunID_20250517_4.csv: Anteil in Merge 9.0%
'''
'''
V2 Abstand 2.5m
Erfolgreich zusammengeführt! Anzahl Bäume: 3631
Datei gespeichert unter: arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\01_v2_baumdaten_watershed_merged.csv

baumdaten_watershed_RunID_20250517_final2.csv: Ursprünglich 3251 Bäume, davon 3250 in der Merge-Datei.
baumdaten_watershed_RunID_20250517_final4.csv: Ursprünglich 3082 Bäume, davon 237 in der Merge-Datei.
baumdaten_watershed_RunID_20250517_4.csv: Ursprünglich 3271 Bäume, davon 144 in der Merge-Datei.
baumdaten_watershed_RunID_20250517_final2.csv: Anteil in Merge 89.5%
baumdaten_watershed_RunID_20250517_final4.csv: Anteil in Merge 6.5%
baumdaten_watershed_RunID_20250517_4.csv: Anteil in Merge 4.0%
'''

file_name = "01_v2_baumdaten_watershed_merged"
# Liste der Merge Dateien
csv_files = [
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_final2\baumdaten_watershed_RunID_20250517_final2.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_final4\baumdaten_watershed_RunID_20250517_final4.csv",
    r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\20250517_4\baumdaten_watershed_RunID_20250517_4.csv",
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
TOLERANZ = 2.5
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
output_path = os.path.join(output_dir, f"{file_name}.csv")
unique_trees.drop(columns=["Quelle"]).to_csv(output_path, index=False)

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
