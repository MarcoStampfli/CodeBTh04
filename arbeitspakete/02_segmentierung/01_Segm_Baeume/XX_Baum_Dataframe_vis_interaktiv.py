import open3d as o3d
import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# 1) Daten & Mesh laden
# ------------------------------------------------------------------
csv_path   = Path(r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\baumdaten_Platte3.csv")
mesh_path  = Path(r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\Version_1.obj")

df   = pd.read_csv(csv_path)
mesh = o3d.io.read_triangle_mesh(str(mesh_path))
mesh.compute_vertex_normals()              # wichtig für Beleuchtung

# ------------------------------------------------------------------
# 2) PBR-Material für das Terrain definieren
# ------------------------------------------------------------------
mat_terrain = o3d.visualization.rendering.MaterialRecord()
mat_terrain.shader      = "defaultLit"     # PBR-Shader
mat_terrain.base_color  = [0.8, 0.8, 0.8, 1.0]   # hellgrau
mat_terrain.base_metallic    = 0.0
mat_terrain.base_roughness   = 0.9              # matt, wenig Glanz
mat_terrain.base_reflectance = 0.5

# ------------------------------------------------------------------
# 3) Fenster & Scene anlegen
# ------------------------------------------------------------------
o3d.visualization.gui.Application.instance.initialize()
vis = o3d.visualization.O3DVisualizer("Terrain & Bäume – PBR Demo", 1280, 720)
vis.show_settings = True  # UI-Panel einblenden

# IBL / Himmel aktivieren (indirekte Beleuchtung)
vis.scene.scene.set_indirect_light_intensity(30_000)
vis.scene.scene.set_sun_light([-0.3, -1, -1], [1, 1, 0.98], 300_000)

# ------------------------------------------------------------------
# 4) Terrain hinzufügen (mit Material)
# ------------------------------------------------------------------
vis.add_geometry("terrain", mesh, mat_terrain)

# ------------------------------------------------------------------
# 5) Bäume aufbauen und in Scene stecken
# ------------------------------------------------------------------
for _, row in df.iterrows():
    x, y, z0 = row["X"], row["Y"], row["Z"]

    # Parameter
    crown_h, crown_d = row["Crown_Height_m"], row["Crown_Diameter_m"]
    trunk_h, trunk_d = row["Trunk_Height_m"], row["Trunk_Diameter_m"]

    # Farben [0-1]
    crown_rgb = [row["Crown_R"]/255, row["Crown_G"]/255, row["Crown_B"]/255]
    trunk_rgb = [row["Trunk_R"]/255, row["Trunk_G"]/255, row["Trunk_B"]/255]

    # Stamm (Zylinder)
    cyl = o3d.geometry.TriangleMesh.create_cylinder(
        radius=trunk_d/2, height=trunk_h, resolution=20, split=4)
    cyl.paint_uniform_color(trunk_rgb)
    cyl.translate((x, y, z0 + trunk_h/2))

    # Krone (Ellipsoid aus Kugel)
    sph = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=20)
    sph.vertices = o3d.utility.Vector3dVector(
        np.asarray(sph.vertices) * np.array([crown_d/2, crown_d/2, crown_h/2]))
    sph.paint_uniform_color(crown_rgb)
    sph.translate((x, y, z0 + trunk_h + crown_h/2))

    # Baum-Geometrien mit einfachem „unlit“-Material (nur Vertex-Farbe)
    mat_unlit          = o3d.visualization.rendering.MaterialRecord()
    mat_unlit.shader   = "defaultUnlit"

    vis.add_geometry(f"trunk_{row.Tree_ID}",  cyl, mat_unlit)
    vis.add_geometry(f"crown_{row.Tree_ID}", sph, mat_unlit)

# ------------------------------------------------------------------
# 6) Beleuchtung: Sonne + weiche Schatten
# ------------------------------------------------------------------
sun_dir = [-0.3, -1.0, -1.0]              # Richtung der Sonne (x,y,z)
vis.scene.scene.set_sun_light(
    sun_dir,                              # Richtung
    [1.0, 1.0, 0.98],                     # Farbe (leicht warm)
    300000.0)                             # Intensität (Lux)
vis.scene.scene.enable_sun_light(True)

vis.scene.scene.set_indirect_light_intensity(30_000)  # IBL-Helligkeit
vis.scene.scene.set_shadow_type(
    o3d.visualization.rendering.Scene.ShadowType.PCF) # weichere Schatten
vis.scene.scene.set_shadow_enabled(True)

# ------------------------------------------------------------------
# 7) Kamera grob positionieren (optional)
# ------------------------------------------------------------------
bbox = mesh.get_axis_aligned_bounding_box()
vis.reset_camera_to_default()
vis.setup_camera(60.0, bbox, bbox.get_center() + [0, 0, 50])

# ------------------------------------------------------------------
# 8) Anzeigen
# ------------------------------------------------------------------
vis.show()
input("Fenster offen lassen – Drücke Enter zum Schließen...")

