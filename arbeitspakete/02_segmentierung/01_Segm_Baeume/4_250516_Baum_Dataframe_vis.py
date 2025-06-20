
# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
"""
Abstract:
Dieses Skript visualisiert eine 3D-Szene bestehend aus einem Gelände-Mesh und modellierten Einzelbäumen. 
Das Terrain wird aus einer OBJ-Datei geladen und einheitlich eingefärbt. Die Baumdaten 
(Position, Stamm- und Kronenparameter, Farben) werden aus einer CSV-Tabelle gelesen. 
Für jeden Baum werden Stamm und Krone als parametrische 3D-Geometrien (Zylinder und skaliertes Ellipsoid) 
im Raum positioniert und farblich codiert. Die komplette Szene kann anschließend interaktiv mit Open3D betrachtet werden. 
Das Skript dient der anschaulichen Qualitätskontrolle und Präsentation von Ergebnissen aus der automatisierten Baumdetektion und -modellierung.
"""

import open3d as o3d
import numpy as np
import pandas as pd

# --- Terrain-Mesh laden und optional färben ---
mesh_output = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Version_1_Mesh_textur.obj"
mesh_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\Version_1.obj"
mesh_legacy = o3d.io.read_triangle_mesh(mesh_path)
# mesh_legacy.paint_uniform_color([0.8, 0.8, 0.8])  # Hellgrau

# --- Daten laden ---
# input_csv = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\baumdaten_Platte3_4244.csv"
input_csv = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\02_v2_baumdaten_Platte3_3631.csv"
df = pd.read_csv(input_csv)

scene = [mesh_legacy]  # Start mit Mesh

for _, row in df.iterrows():
    x, y, z0 = row["X"], row["Y"], row["Z"]
    crown_height   = row["Crown_Height_m"]
    crown_diameter = row["Crown_Diameter_m"]
    trunk_height   = row["Trunk_Height_m"]
    trunk_diam     = row["Trunk_Diameter_m"]

    crown_rgb = [row["Crown_R"]/255.0, row["Crown_G"]/255.0, row["Crown_B"]/255.0]
    trunk_rgb = [row["Trunk_R"]/255.0, row["Trunk_G"]/255.0, row["Trunk_B"]/255.0]

    # Stamm als Zylinder
    cyl = o3d.geometry.TriangleMesh.create_cylinder(
        radius=trunk_diam/2.0, height=trunk_height,
        resolution=20, split=4
    )
    cyl.paint_uniform_color(trunk_rgb)
    cyl.translate((x, y, z0 + trunk_height/2.0))

    # Krone als Ellipsoid
    sph = o3d.geometry.TriangleMesh.create_sphere(
        radius=1.0, resolution=20
    )
    sph.vertices = o3d.utility.Vector3dVector(
        np.asarray(sph.vertices) * np.array([
            crown_diameter/2.0,
            crown_diameter/2.0,
            crown_height/2.0
        ])
    )
    sph.paint_uniform_color(crown_rgb)
    sph.translate((x, y, z0 + trunk_height + crown_height/2.0))

    scene.append(cyl)
    scene.append(sph)

o3d.visualization.draw_geometries(
    scene,
    window_name="Terrain & Bäume",
    width=1280, height=720,
    mesh_show_back_face=True
)
