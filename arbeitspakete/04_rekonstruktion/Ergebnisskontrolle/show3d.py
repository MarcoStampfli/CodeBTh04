import open3d as o3d
import os

def visualize_3d_file(file_path):
    # Prüfen, ob Datei existiert
    if not os.path.isfile(file_path):
        print(f"Datei nicht gefunden: {file_path}")
        return

    # Dateiendung bestimmen
    ext = os.path.splitext(file_path)[-1].lower()

    # Mesh-Dateien
    if ext in [".obj", ".ply"]:
        mesh = o3d.io.read_triangle_mesh(file_path)
        if mesh.has_vertices():
            mesh.compute_vertex_normals()
            print(f"Lade Mesh aus {file_path}")
            o3d.visualization.draw_geometries([mesh])
            return
        # Falls kein Mesh, aber vielleicht eine Punktwolke (z.B. bei PLY)
    # Punktwolken-Dateien
    if ext in [".pcd", ".ply"]:
        pcd = o3d.io.read_point_cloud(file_path)
        if pcd.has_points():
            print(f"Lade Punktwolke aus {file_path}")
            o3d.visualization.draw_geometries([pcd])
            return

    print("Dateiformat oder Inhalt wird nicht unterstützt (.obj, .ply, .pcd)")

if __name__ == "__main__":
    file_path = input(r"C:\Users\st1174360\Desktop\2.obj").strip()
    visualize_3d_file(file_path)

