import open3d as o3d
import numpy as np

# Dateipfade
mesh_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\Mesh_Boden.obj"
pc_csv_path = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\input\Boden.csv"
mesh_output = r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Version_1_Mesh_textur.obj"

# Punktwolke aus CSV laden (XYZRGB, z.B. als 6 Spalten)
data = np.loadtxt(pc_csv_path, delimiter=';')
points = data[:, 0:3]
colors = data[:, 3:6]

# Wenn die Farben in 0-255 sind, auf 0-1 normieren:
if colors.max() > 1.0:
    colors = colors / 255.0

# Punktwolke in Open3D-Objekt umwandeln
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

# Mesh laden
mesh = o3d.io.read_triangle_mesh(mesh_path)
mesh.compute_vertex_normals()

# KDTree für Punktwolke
pcd_tree = o3d.geometry.KDTreeFlann(pcd)

# Farben auf Mesh-Vertices übertragen
radius = 0.5  # z.B. 5 cm (anpassen je nach Maßstab)
mesh_colors = []
for v in mesh.vertices:
    [_, idx, _] = pcd_tree.search_radius_vector_3d(v, radius)
    if len(idx) > 0:
        colors_neigh = np.asarray(pcd.colors)[idx]
        mean_color = np.mean(colors_neigh, axis=0)
        mesh_colors.append(mean_color)
    else:
        # Fallback: Standardfarbe, z.B. grau
        mesh_colors.append([0.5, 0.5, 0.5])
mesh.vertex_colors = o3d.utility.Vector3dVector(np.array(mesh_colors))


# Mesh speichern
o3d.io.write_triangle_mesh(mesh_output, mesh, write_vertex_colors=True)
print(f"Gefärbtes Mesh gespeichert unter: {mesh_output}")

# Visualisierung und Screenshot
vis = o3d.visualization.Visualizer()
vis.create_window(visible=True)
vis.add_geometry(mesh)
vis.poll_events()
vis.update_renderer()
vis.capture_screen_image("screenshot_mesh.png")
vis.run()
vis.destroy_window()
print("Screenshot gespeichert als screenshot_mesh.png")
