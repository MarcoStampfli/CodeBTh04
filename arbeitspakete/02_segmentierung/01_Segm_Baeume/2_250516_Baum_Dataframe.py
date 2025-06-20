# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
'''
INPUT: Roh CSV-Datei Bäume, Mesh
OUTPUT: CSV mit Baumparameter für Modellierung
'''
'''
Das Skript berechnet für jede Baumposition aus einer CSV-Datei auf Basis eines Gelände-Meshs die Baumhöhe (Abstand Baumspitze zum Gelände)
und leitet daraus alle Parameter ab, die für eine 3D-Modellierung der Bäume (z. B. für Visualisierung oder Simulation) benötigt werden. 
Die Resultate werden in eine neue CSV geschrieben.
'''

import open3d as o3d
import numpy as np
import pandas as pd
import os

# Parameter
input_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\01_v3_baumdaten_watershed_merged.csv"
# -----
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)
# -----
file_name_output = "02_v3_baumdaten_Platte3_5309.csv"

# --- 1. CSV mit den Baum-Koordinaten laden ---
df = pd.read_csv(input_path, delimiter=",", decimal=".")
# Spaltennamen anpassen, falls nötig:
df.columns = ["Tree_ID", "X", "Y", "Z", "Crown_Diameter_m"]

# --- 2. Terrain-Mesh laden und in die Tensor-API überführen ---
input_path_mesh = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\Version_1.obj"
# input_path_mesh = r"arbeitspakete\02_segmentierung\01_Segm_Bäume\input\Version_1.mtl"

mesh_legacy = o3d.io.read_triangle_mesh(input_path_mesh)
mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh_legacy)

# --- 3. Raycasting-Szene aufbauen ---
scene = o3d.t.geometry.RaycastingScene()
_ = scene.add_triangles(mesh)

# --- 4. Baum-Punkte als Rays definieren ---
# Ursprung = jeder Baum-Punkt; Richtung = nach unten (0,0,–1)
points_np = df[["X", "Y", "Z"]].to_numpy(dtype=np.float32)  # shape [N,3]
dirs_np   = np.tile([0, 0, -1], (points_np.shape[0], 1)).astype(np.float32)
# Tensor aus [orig_x, orig_y, orig_z, dir_x, dir_y, dir_z]
rays = o3d.core.Tensor(
    np.hstack((points_np, dirs_np)),
    dtype=o3d.core.Dtype.Float32
)

# --- 5. Strahlen abfeuern und t_hit auslesen ---
ans   = scene.cast_rays(rays)
t_hit = ans["t_hit"].numpy()    # array der lotrechten Distanzen, shape [N]

# --- 6. Ergebnis ins DataFrame schreiben ---
df["Tree_Height_m"] = np.round(t_hit, 2)

# --- Z neu berechnen (Z = Original-Z minus height_m)
df["Z"] = df["Z"] - df["Tree_Height_m"]

# --- Kronen und Stamm Parameter berechnen
df["Crown_Height_m"] = 2/3 * df["Tree_Height_m"]
df["Trunk_Height_m"] = 1/3 * df["Tree_Height_m"]
df["Trunk_Diameter_m"] = 1/6 * df["Crown_Diameter_m"]

# --- Farben definieren
crown_color = [42.0, 49.0, 46.0]
trunk_color = [139.0, 69.0, 19.0]

df["Crown_RGB"] = [crown_color] * len(df)
df["Trunk_RGB"] = [trunk_color] * len(df)
# Wandlung einmalig beim Erstellen
df[["Crown_R","Crown_G","Crown_B"]] = pd.DataFrame(df["Crown_RGB"].tolist(), index=df.index)
df.drop(columns=["Crown_RGB"], inplace=True)
df[["Trunk_R","Trunk_G","Trunk_B"]] = pd.DataFrame(df["Trunk_RGB"].tolist(), index=df.index)
df.drop(columns=["Trunk_RGB"], inplace=True)

# --- Spalten in die gewünschte Reihenfolge bringen
# Baumparameter
df = df[[
    "Tree_ID",
    "X",
    "Y",
    "Z",
    "Tree_Height_m",
    "Crown_Height_m",
    "Crown_Diameter_m",
    "Trunk_Height_m",
    "Trunk_Diameter_m",
    "Crown_R","Crown_G","Crown_B",
    "Trunk_R","Trunk_G","Trunk_B"
]]

# --- 7. Ergebnisse sichern ---
output_path = os.path.join(output_dir, file_name_output)
df.to_csv(output_path, index=False)

print("Fertig: ", output_path, "gespeichert.")
