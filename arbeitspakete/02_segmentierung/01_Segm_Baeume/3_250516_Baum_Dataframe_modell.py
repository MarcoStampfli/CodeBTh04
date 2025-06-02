'''
Das Skript nimmt eine Tabelle mit Baumparametern (Position, Höhe, Kronendurchmesser, Stammhöhe, Stammfarbe usw.) 
und erzeugt für jeden Baum ein 3D-Modell aus Zylinder (Stamm) und Ellipsoid (Krone).
Am Ende werden alle Bäume zu einem Gesamt-Mesh vereinigt und in verschiedene 
3D-Formate (OBJ, PLY, optional STL) exportiert, zusätzlich ist eine direkte 3D-Visualisierung möglich.
'''
import open3d as o3d
import numpy as np
import pandas as pd
import os

# --- Daten laden ---
# input_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\02_baumdaten_Platte3_4244.csv"
input_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\02_v2_baumdaten_Platte3_3631.csv"
# input_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten\02_v3_baumdaten_Platte3_5309.csv"
# input_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten_Platte3.csv"
df = pd.read_csv(input_path)

# Auflösung der Geometrie default 20
resolution=6

file_name = f"03_v3_baummodel_Platte3_5309_Aufl_{resolution}"
output_dir = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Baumdaten"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, file_name)
# Wir bauen ein Mesh für alle Bäume
all_baeume = o3d.geometry.TriangleMesh()

for _, row in df.iterrows():
    x, y, z0 = row["X"], row["Y"], row["Z"]

    # Parameter
    crown_h, crown_d = row["Crown_Height_m"], row["Crown_Diameter_m"]
    trunk_h, trunk_d = row["Trunk_Height_m"], row["Trunk_Diameter_m"]

    crown_rgb = [row["Crown_R"]/255, row["Crown_G"]/255, row["Crown_B"]/255]
    trunk_rgb = [row["Trunk_R"]/255, row["Trunk_G"]/255, row["Trunk_B"]/255]

    # Stamm (Zylinder)
    cyl = o3d.geometry.TriangleMesh.create_cylinder(radius=trunk_d/2, height=trunk_h, resolution=resolution)
    cyl.paint_uniform_color(trunk_rgb)
    cyl.translate((x, y, z0 + trunk_h/2))

    # Krone (Ellipsoid)
    sph = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=resolution)
    sph.vertices = o3d.utility.Vector3dVector(
        np.asarray(sph.vertices) * np.array([crown_d/2, crown_d/2, crown_h/2])
    )
    sph.paint_uniform_color(crown_rgb)
    sph.translate((x, y, z0 + trunk_h + crown_h/2))

    # Stamm und Krone kombinieren (addiert Vertices & Faces!)
    tree_mesh = cyl + sph

    # Addiere zu Gesamtmesh
    all_baeume += tree_mesh



output_path = os.path.join(output_dir, file_name)
# --- Export als OBJ ---
o3d.io.write_triangle_mesh(f"{output_path}.obj", all_baeume)
print("Exportiert als baum_modelle.obj")

# --- Export als PLY ---
o3d.io.write_triangle_mesh(f"{output_path}.ply", all_baeume)
print("Exportiert als baum_modelle.ply")

# --- Export als STL --- ohne Farben!!! gut für 3D-Druck
# o3d.io.write_triangle_mesh(f"{output_path}.stl", all_baeume)
# print("Exportiert als baum_modelle.stl")

# --- Optional: Visualisierung ---
o3d.visualization.draw_geometries([all_baeume])
