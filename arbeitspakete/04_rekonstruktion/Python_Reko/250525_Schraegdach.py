
''' Ansatz nach Literatur https://arxiv.org/pdf/2201.01191 siehe dazu Abbildung 2 + Text dazu.'''


import os
import laspy
import numpy as np
import open3d as o3d
import trimesh
from shapely.geometry import Polygon
from shapely.ops import triangulate as shapely_triangulate
from scipy.spatial import Delaunay, cKDTree

# ----------------------------
# Hilfsfunktion
# ----------------------------
def project_to_plane(pts, plane):
    """Projiziert pts (N×3) in 2D in die Ebene ax+by+cz+d=0 und gibt (pts2d, center, u, v)."""
    a, b, c, d = plane
    n = np.array([a, b, c]); n /= np.linalg.norm(n)
    arb = np.array([0,0,1]) if abs(n[2])<0.9 else np.array([1,0,0])
    u = np.cross(n, arb); u /= np.linalg.norm(u)
    v = np.cross(n, u);   v /= np.linalg.norm(v)
    center = pts.mean(axis=0)
    rel = pts - center
    pts2d = np.vstack((rel.dot(u), rel.dot(v))).T
    return pts2d, center, u, v

# ----------------------------
# Config
# ----------------------------
las_path        = r"arbeitspakete\04_rekonstruktion\Python_Reko\input\180_1_Walmdach.las"
dachtyp         = "Walmdach"
percent_inliers = 0.02    # 2 % der Dachpunkte als min_inliers
thresh_factor   = 1.5     # Faktor auf median point-spacing
max_planes      = 8       # Max. Ebenen

# ----------------------------
# 1) LAS laden & Boden segmentieren
# ----------------------------
las  = laspy.read(las_path)
pts  = np.vstack((las.x, las.y, las.z)).T
pcd  = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))

# Bodenebene per RANSAC
plane_ground, inds_ground = pcd.segment_plane(0.05, 3, 1000)
ground_pts = np.asarray(pcd.points)[inds_ground]
roof_pts   = np.delete(np.asarray(pcd.points), inds_ground, axis=0)
roof_count = len(roof_pts)

# ----------------------------
# 2) Footprint aus 1 m-Slice
# ----------------------------
ground_z  = np.median(ground_pts[:,2])
slice_z   = ground_z + 1.0
slice_tol = 0.05  # wird später automatisch gesetzt
idx = np.where((pts[:,2] >= slice_z - slice_tol) & (pts[:,2] <= slice_z + slice_tol))[0]
xy = pts[idx,:2]

if len(xy) >= 3:
    hull = Delaunay(xy).convex_hull.reshape(-1)
    hull_xy = xy[np.unique(hull)]
    footprint = Polygon(hull_xy).convex_hull
    print(f"Footprint aus {len(xy)} Slice-Punkten bei {slice_z:.2f} m")
else:
    print("Zu wenige Slice-Punkte – Fallback auf Boden-Footprint")
    xy = ground_pts[:,:2]
    hull = Delaunay(xy).convex_hull.reshape(-1)
    hull_xy = xy[np.unique(hull)]
    footprint = Polygon(hull_xy).convex_hull

# ----------------------------
# 3) Auto-Thresholds
# ----------------------------
tree = cKDTree(roof_pts)
d, _ = tree.query(roof_pts, k=2)
median_spacing     = np.median(d[:,1])
distance_threshold = median_spacing * thresh_factor
min_inliers        = max(10, int(roof_count * percent_inliers))

# setze slice_tol für Footprint-Fallback realistisch
slice_tol = distance_threshold

print(f"Dachpunkte: {roof_count}, threshold: {distance_threshold:.3f}, min_inliers: {min_inliers}")

# ----------------------------
# 4) RANSAC-Dachsegmentierung
# ----------------------------
roof_pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(roof_pts))
plane_segments = []
for _ in range(max_planes):
    if len(roof_pcd.points) < min_inliers:
        break
    model, inds = roof_pcd.segment_plane(distance_threshold, 3, 1000)
    if len(inds) < min_inliers:
        break
    n = np.array(model[:3]); n /= np.linalg.norm(n)
    if 0.2 < abs(n[2]) < 0.95:
        seg = roof_pcd.select_by_index(inds)
        plane_segments.append((seg, model))
    roof_pcd = roof_pcd.select_by_index(inds, invert=True)

# ----------------------------
# 5) Triangulation über Hüllkurve (Variante A)
# ----------------------------
roof_tris = []
for seg, model in plane_segments:
    pts3d = np.asarray(seg.points)
    pts2d, center, u, v = project_to_plane(pts3d, model)
    poly2d = Polygon(pts2d).convex_hull
    tris2d = shapely_triangulate(poly2d)
    verts, faces = [], []
    for t in tris2d:
        coords2d = np.array(t.exterior.coords)[:3]
        # zurück projizieren auf 3D
        tri3d = center + np.outer(coords2d[:,0], u) + np.outer(coords2d[:,1], v)
        start  = len(verts)
        verts.extend(tri3d)
        faces.append([start, start+1, start+2])
    roof_tris.append(trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces)))

# ----------------------------
# 6) Wand‐Extrusion
# ----------------------------
wall_height = roof_pts[:,2].min() - ground_pts[:,2].max()
wall_mesh   = trimesh.creation.extrude_polygon(footprint, height=wall_height)

# ----------------------------
# 7) Export & Visualisierung
# ----------------------------
# Mesh zusammenführen
full_mesh = trimesh.util.concatenate(roof_tris + [wall_mesh])

# Pfad anlegen
dateiname  = os.path.splitext(os.path.basename(las_path))[0]
out_dir    = rf"arbeitspakete\04_rekonstruktion\Python_Reko\output\{dachtyp}"
os.makedirs(out_dir, exist_ok=True)
out_path   = os.path.join(out_dir, f"{dateiname}.ply")
out_path   = os.path.join(out_dir, f"{dateiname}.obj")

full_mesh.export(out_path)
print(f"Erfolgreich exportiert nach:\n  {out_path}")

# (Optional) zum schnellen Check:
o3d_meshes = []
for part in roof_tris + [wall_mesh]:
    m = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(part.vertices),
        o3d.utility.Vector3iVector(part.faces)
    )
    m.compute_vertex_normals()
    color = np.array([76.6,57.7,57])/255 if part in roof_tris else np.array([98.8,94,93])/255
    m.paint_uniform_color(color)
    o3d_meshes.append(m)

o3d.visualization.draw_geometries(o3d_meshes,
                                  window_name="Walmdach (var. A)",
                                  mesh_show_back_face=True)
