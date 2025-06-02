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
# Utils
# ----------------------------
def project_to_plane(pts, plane):
    """Projiziert 3D-Punkte auf Ebene ax+by+cz+d=0 und liefert 2D-Coords + Basisvektoren."""
    a, b, c, d = plane
    n = np.array([a, b, c]); n /= np.linalg.norm(n)
    arb = np.array([0,0,1]) if abs(n[2])<0.9 else np.array([1,0,0])
    u = np.cross(n, arb); u /= np.linalg.norm(u)
    v = np.cross(n, u);   v /= np.linalg.norm(v)
    center = pts.mean(axis=0)
    rel = pts - center
    pts2d = np.vstack((rel.dot(u), rel.dot(v))).T
    return pts2d, center, u, v

def planarize_segments(pcd, distance_threshold, min_inliers, normal_filter, max_planes):
    """
    Führt RANSAC-Plane auf pcd durch, filtert nach normal_filter(normal) → bool,
    gibt Liste von (PointCloud-Segment, plane_model).
    """
    segments = []
    remaining = pcd
    for _ in range(max_planes):
        if len(remaining.points) < min_inliers:
            break
        model, inds = remaining.segment_plane(distance_threshold, 3, 1000)
        if len(inds) < min_inliers:
            break
        n = np.array(model[:3]); n /= np.linalg.norm(n)
        if normal_filter(n):
            seg = remaining.select_by_index(inds)
            segments.append((seg, model))
        remaining = remaining.select_by_index(inds, invert=True)
    return segments, remaining

def triangulate_planar_segment(seg, model):
    """
    Nimmt einen Punkt-Cloud-Segment und sein Ebenenmodell,
    erstellt aus der konvexen Hüllkurve ein Trimesh.
    """
    pts3d = np.asarray(seg.points)
    pts2d, center, u, v = project_to_plane(pts3d, model)
    poly2d = Polygon(pts2d).convex_hull
    tris2d = shapely_triangulate(poly2d)
    verts, faces = [], []
    for tri in tris2d:
        coords2d = np.array(tri.exterior.coords)[:3]
        tri3d = center + np.outer(coords2d[:,0], u) + np.outer(coords2d[:,1], v)
        idx0 = len(verts)
        verts.extend(tri3d)
        faces.append([idx0, idx0+1, idx0+2])
    return trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces))


# ----------------------------
# Config
# ----------------------------
las_path      = r"arbeitspakete\04_rekonstruktion\Python_Reko\input\250517_Gebäude_Attribut\Satteldach\1_Satteldach\140_1_Satteldach.las"
dachtyp       = "Walmdach"
percent_in    = 0.02       # 2 % der Dachpunkte
thresh_factor = 1.5        # Faktor auf median point-spacing
max_planes    = 4

# ----------------------------
# 1) LAS laden & Boden filtern
# ----------------------------
las   = laspy.read(las_path)
pts   = np.vstack((las.x, las.y, las.z)).T
pcd   = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))
# RANSAC-Boden
_, inds_ground = pcd.segment_plane(0.05, 3, 1000)
ground_pts     = np.asarray(pcd.points)[inds_ground]
roof_pts       = np.delete(np.asarray(pcd.points), inds_ground, axis=0)
roof_count     = len(roof_pts)

# ----------------------------
# 2) Footprint aus 1m-Slice
# ----------------------------
ground_z = np.median(ground_pts[:,2])
slice_z  = ground_z + 1.0
# Slice-Toleranz später auf distance_threshold gesetzt
slice_tol = 0.05
idx = np.where((pts[:,2] >= slice_z-slice_tol) & (pts[:,2] <= slice_z+slice_tol))[0]
xy  = pts[idx,:2]
if len(xy) >= 3:
    hull = Delaunay(xy).convex_hull.reshape(-1)
    hull_xy = xy[np.unique(hull)]
    footprint = Polygon(hull_xy).convex_hull
else:
    xy = ground_pts[:,:2]
    hull = Delaunay(xy).convex_hull.reshape(-1)
    hull_xy = xy[np.unique(hull)]
    footprint = Polygon(hull_xy).convex_hull

# ----------------------------
# 3) Auto-Thresholds
# ----------------------------
tree = cKDTree(roof_pts)
d, _ = tree.query(roof_pts, k=2)
median_sp    = np.median(d[:,1])
dist_th      = median_sp * thresh_factor
min_inliers  = max(50, int(roof_count * percent_in))
slice_tol    = dist_th

# ----------------------------
# 4) Dach-Segmentierung (geneigte Flächen)
# ----------------------------
roof_pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(roof_pts))
roof_segments, roof_remain = planarize_segments(
    roof_pcd, dist_th, min_inliers,
    normal_filter=lambda n: 0.2 < abs(n[2]) < 0.95,
    max_planes=max_planes
)

# ----------------------------
# 5) Wand-Segmentierung (vertikale Flächen)
# ----------------------------
# Als Wand­punkte nutzen wir roof_remain (alles, was nicht Dach war)
wall_segments, wall_remain = planarize_segments(
    roof_remain, dist_th, min_inliers,
    normal_filter=lambda n: abs(n[2]) < 0.19,
    max_planes=max_planes
)

# ----------------------------
# 6) Triangulation der Segmente
# ----------------------------
roof_tris = [triangulate_planar_segment(seg, mdl) for seg, mdl in roof_segments]
wall_tris = [triangulate_planar_segment(seg, mdl) for seg, mdl in wall_segments]

# Fallback: wenn keine Wandsegmente, extrudiere Footprint
if not wall_tris:
    wall_height = roof_pts[:,2].min() - ground_pts[:,2].max()
    wall_tris.append(trimesh.creation.extrude_polygon(footprint, height=wall_height))

# ----------------------------
# 7) Kombiniere & exportiere
# ----------------------------
full = trimesh.util.concatenate(roof_tris + wall_tris)

# Output-Pfad
dateiname = os.path.splitext(os.path.basename(las_path))[0]
out_dir   = rf"arbeitspakete\04_rekonstruktion\Python_Reko\output\{dachtyp}"
os.makedirs(out_dir, exist_ok=True)
out_path  = os.path.join(out_dir, f"{dateiname}.ply")

full.export(out_path)
print(f"Exportiert nach: {out_path}")

# ----------------------------
# 8) (Optional) Schnell-Visualisierung: PW + plane Meshes
# ----------------------------
# 8a) Punktwolke in Orange
pcd_vis = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))
orange = np.array([1.0, 0.5, 0.0])  # RGB in [0..1]
pcd_vis.paint_uniform_color(orange)

# 8b) Dach- und Fassaden-Meshes
o3d_meshes = [pcd_vis]
col_roof = np.array([76.6,57.7,57])/255.0
col_wall = np.array([98.8,94,93])/255.0

for m in roof_tris:
    om = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(m.vertices),
        o3d.utility.Vector3iVector(m.faces)
    )
    om.compute_vertex_normals()
    om.paint_uniform_color(col_roof)
    o3d_meshes.append(om)

for m in wall_tris:
    om = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(m.vertices),
        o3d.utility.Vector3iVector(m.faces)
    )
    om.compute_vertex_normals()
    om.paint_uniform_color(col_wall)
    o3d_meshes.append(om)

# 8c) alles auf einmal anzeigen
o3d.visualization.draw_geometries(
    o3d_meshes,
    window_name="Punktwolke (orange) + plane Dächer/Wände",
    mesh_show_back_face=True
)
