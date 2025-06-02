''' Ansatz nach Literatur https://arxiv.org/pdf/2201.01191 siehe dazu Abbildung 2 + Text dazu.'''

import os
import laspy
import numpy as np
import open3d as o3d
import trimesh
from shapely.geometry import Polygon, LineString, MultiLineString, MultiPoint, GeometryCollection
from shapely.ops import split, unary_union, triangulate as shapely_triangulate
from shapely.errors import GeometryTypeError
from scipy.spatial import Delaunay, cKDTree
from itertools import combinations

# -----------------------------------
# Hilfsfunktionen
# -----------------------------------
def project_to_plane(pts, plane):
    a,b,c,d = plane
    n = np.array([a,b,c]); n /= np.linalg.norm(n)
    arb = np.array([0,0,1]) if abs(n[2])<0.9 else np.array([1,0,0])
    u = np.cross(n, arb); u /= np.linalg.norm(u)
    v = np.cross(n, u);   v /= np.linalg.norm(v)
    center = pts.mean(axis=0)
    rel = pts - center
    pts2d = np.vstack((rel.dot(u), rel.dot(v))).T
    return pts2d, center, u, v

def detect_roof_planes(roof_pts, dist_th, min_inliers, max_planes=8):
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(roof_pts))
    segments = []
    for _ in range(max_planes):
        if len(pcd.points) < min_inliers:
            break
        model, inds = pcd.segment_plane(dist_th, 3, 1000)
        if len(inds) < min_inliers:
            break
        n = np.array(model[:3]); n /= np.linalg.norm(n)
        if 0.2 < abs(n[2]) < 0.95:  # nur geneigte
            seg = pcd.select_by_index(inds)
            segments.append((np.asarray(seg.points), model))
        pcd = pcd.select_by_index(inds, invert=True)
    return segments

def build_alpha_polygons(roof_segments):
    polys = []
    for pts3d, model in roof_segments:
        xy = pts3d[:, :2]
        if len(xy) < 3:
            continue
        poly = MultiPoint(xy).convex_hull
        polys.append((poly, model))
    return polys

def extract_partition_lines(roof_polys):
    lines = []
    # boundary
    for poly, _ in roof_polys:
        lines.append(poly.exterior)
    # intersections
    for (p1,m1),(p2,m2) in combinations(roof_polys,2):
        inter = p1.intersection(p2)
        if inter.is_empty:
            continue
        if isinstance(inter, LineString):
            lines.append(inter)
        elif isinstance(inter, MultiLineString):
            lines.extend(inter.geoms)
    return unary_union(lines)

def initial_roof_partition(footprint, union_lines):
    # extrahiere einzelne LineStrings
    if hasattr(union_lines, "geoms"):
        lines = [g for g in union_lines.geoms if isinstance(g, LineString)]
    elif isinstance(union_lines, LineString):
        lines = [union_lines]
    else:
        lines = []
    faces = [footprint]
    for line in lines:
        new = []
        for face in faces:
            try:
                out = split(face, line)
                parts = list(out.geoms) if hasattr(out, "geoms") else [out]
                new.extend(parts)
            except GeometryTypeError:
                new.append(face)
        faces = new
    return faces

def assign_faces_to_planes(faces, roof_segments, roof_pts):
    face_model = {}
    for face in faces:
        cx, cy = face.centroid.x, face.centroid.y
        dxy = np.linalg.norm(roof_pts[:,:2] - [cx, cy], axis=1)
        p3d = roof_pts[np.argmin(dxy)]
        best, md = None, np.inf
        for _,model in roof_segments:
            a,b,c,d = model
            dist = abs(a*p3d[0]+b*p3d[1]+c*p3d[2]+d)/np.linalg.norm([a,b,c])
            if dist < md:
                md, best = dist, model
        if best is not None:
            face_model[face] = best
    merged = {}
    for face,model in face_model.items():
        key = tuple(model)
        merged.setdefault(key, []).append(face)
    parts = [unary_union(grp) for grp in merged.values()]
    models = [np.array(key) for key in merged.keys()]
    return parts, models

def triangulate_parts(parts, models):
    """
    Trianguliert jede finale Roof-Part (2D-Polygon) planar in die jeweilige 3D-Ebene.
    """
    meshes = []
    for poly, model in zip(parts, models):
        # 2D-Triangulation des Polygons
        tris2d = shapely_triangulate(poly)
        for t in tris2d:
            # hole die ersten 3 Ecken (x,y)
            coords2d = np.array(t.exterior.coords)[:3]  # shape (3,2)
            # erweitere um eine Z-Komponente = 0
            pts3d_plane = np.column_stack((coords2d[:,0], coords2d[:,1], np.zeros(len(coords2d))))
            # projiziere in die Ebene
            pts2d, center, u, v = project_to_plane(pts3d_plane, model)
            # zurück in 3D
            tri3d = center + np.outer(pts2d[:,0], u) + np.outer(pts2d[:,1], v)
            meshes.append(trimesh.Trimesh(vertices=tri3d, faces=[[0,1,2]]))
    return meshes


# -----------------------------------
# Main
# -----------------------------------
las_path  = r"arbeitspakete\04_rekonstruktion\Python_Reko\input\180_1_Walmdach.las"
dachtyp   = "Walmdach"

# 1) Einlesen & Boden per RANSAC entfernen
las = laspy.read(las_path)
pts = np.vstack((las.x, las.y, las.z)).T
pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))
_,inds = pcd.segment_plane(0.05, 3, 1000)
ground = np.asarray(pcd.points)[inds]
roof   = np.delete(np.asarray(pcd.points), inds, axis=0)

# 2) Footprint aus 1 m-Slice
ground_z = np.median(ground[:,2])
slice_z  = ground_z + 1.0
tol      = 0.05
idx      = np.where((pts[:,2] >= slice_z-tol)&(pts[:,2] <= slice_z+tol))[0]
xy       = pts[idx,:2]
if len(xy) >= 3:
    hull = Delaunay(xy).convex_hull.reshape(-1)
    fp   = Polygon(xy[np.unique(hull)]).convex_hull
else:
    hull = Delaunay(ground[:,:2]).convex_hull.reshape(-1)
    fp   = Polygon(ground[np.unique(hull),:2]).convex_hull

# 3) Automatische Parameter
tree           = cKDTree(roof)
d,_            = tree.query(roof, k=2)
dist_th        = np.median(d[:,1]) * 1.5
min_inliers    = max(50, int(len(roof)*0.02))

# 4) Dach-Ebenen detektieren
roof_segs = detect_roof_planes(roof, dist_th, min_inliers)

# 5) 2D-Polygone (Convex Hull)
roof_polys = build_alpha_polygons(roof_segs)

# 6) Linien extrahieren & Footprint teilen
lines_union    = extract_partition_lines(roof_polys)
initial_faces  = initial_roof_partition(fp, lines_union)

# 7) Zuordnung & Merge
final_faces, final_models = assign_faces_to_planes(initial_faces, roof_segs, roof)

# 8) Triangulation Dach-Teile
roof_meshes = triangulate_parts(final_faces, final_models)

# 9) Wand-Extrusion mit ground_z-Offset
roof_max_z   = roof[:,2].max()
wall_h       = roof_max_z - ground_z
wall_mesh    = trimesh.creation.extrude_polygon(fp, height=wall_h)
wall_mesh.apply_translation((0,0,ground_z))

# 10) Export 3D-Mesh
all_meshes = roof_meshes + [wall_mesh]
full       = trimesh.util.concatenate(all_meshes)
fn         = os.path.splitext(os.path.basename(las_path))[0]
out_dir    = rf"arbeitspakete\04_rekonstruktion\Python_Reko\output\{dachtyp}"
os.makedirs(out_dir, exist_ok=True)
out_3d     = os.path.join(out_dir, f"{fn}.ply")
full.export(out_3d)
print(f"3D-Model exportiert nach:\n  {out_3d}")

# 11) Export Footprint als Grundriss
tris2d = shapely_triangulate(fp)
verts, faces = [], []
for tri in tris2d:
    coords2d = np.array(tri.exterior.coords)[:3]
    for x,y in coords2d:
        verts.append([x,y, ground_z])
    i = len(verts) - 3
    faces.append([i, i+1, i+2])
fp_mesh = trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces))
out_fp   = os.path.join(out_dir, f"{fn}_Grundriss.ply")
fp_mesh.export(out_fp)
print(f"Grundriss exportiert nach:\n  {out_fp}")

# -----------------------------------
# Visualization Block
# -----------------------------------
# a) Punktwolke orange
pcd_vis = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))
pcd_vis.paint_uniform_color([1.0,0.5,0.0])

# b) Dach-Meshes
roof_o3d = []
for m in roof_meshes:
    om = o3d.geometry.TriangleMesh(
        vertices=o3d.utility.Vector3dVector(m.vertices),
        triangles=o3d.utility.Vector3iVector(m.faces)
    )
    om.compute_vertex_normals()
    om.paint_uniform_color(np.array([76.6,57.7,57])/255.0)
    roof_o3d.append(om)

# c) Wand-Mesh
wall_o3d = o3d.geometry.TriangleMesh(
    vertices=o3d.utility.Vector3dVector(wall_mesh.vertices),
    triangles=o3d.utility.Vector3iVector(wall_mesh.faces)
)
wall_o3d.compute_vertex_normals()
wall_o3d.paint_uniform_color(np.array([98.8,94.0,93.0])/255.0)

# d) Grundriss-Mesh in Rot
fp_o3d = o3d.geometry.TriangleMesh(
    vertices=o3d.utility.Vector3dVector(fp_mesh.vertices),
    triangles=o3d.utility.Vector3iVector(fp_mesh.faces)
)
fp_o3d.compute_vertex_normals()
fp_o3d.paint_uniform_color([1.0,0.0,0.0])

# e) Anzeige
o3d.visualization.draw_geometries(
    [pcd_vis] + roof_o3d + [wall_o3d, fp_o3d],
    window_name="PW (orange) + Plane Dächer, Wände & Grundriss",
    mesh_show_back_face=True,
    width=1024, height=768
)
