import open3d as o3d
# ----------------------
# 7. CHM Visualisierung
# ----------------------
print("Visualisiere CHM + Baumgipfel (farblich nach Kronendurchmesser) ...")
plt.figure(figsize=(10, 8))
plt.imshow(chm.T, cmap='viridis', origin='lower',
           extent=[y_min, y_max, x_min, x_max])

# Umrechnung lokaler Maxima in Weltkoordinaten
x_coords = x_min + local_max[:, 1] * res
y_coords = y_min + local_max[:, 0] * res

# Für jedes lokale Maximum den zugehörigen Segment-Label holen
max_labels = labels[local_max[:, 0], local_max[:, 1]]

# Und damit den Crown-Diameter aus dem DataFrame zuordnen
# Achtung: Tree_IDs beginnen ab 1!
diameters = []
for lbl in max_labels:
    entry = df[df["Tree_ID"] == lbl]
    if not entry.empty:
        diameters.append(entry["Crown_Diameter_m"].values[0])
    else:
        diameters.append(np.nan)
diameters = np.array(diameters)

# Scatter mit Farbcodierung
sc = plt.scatter(y_coords, x_coords, c=diameters, cmap='Greens', s=20, edgecolor='k', label="Baumgipfel")
plt.colorbar(sc, label='Durchmesser Baumkrone [m]')
plt.title("CHM mit Baumgipfeln (farbcodiert nach Kronendurchmesser)")
plt.legend()
fig_path = os.path.join(output_dir, f"chm_baumgipfel_colordiameter_RunID_{RunID}.png")
plt.savefig(fig_path, dpi=300)
print(f"CHM gespeichert: {fig_path}")
# Entweder blockierend:
# plt.show()

# ----------------------
# 8. Open3D-Visualisierung mit Screenshot + stabiler Kamera
# ----------------------

print("Starte 3D-Visualisierung ...")

# Punktwolke übernehmen (keine Spiegelung)
filtered_points_trans = np.copy(filtered_points)
filtered_points_trans[:, 0] = filtered_points[:, 0]  # Y → X
filtered_points_trans[:, 1] = filtered_points[:, 1]  # X → Y

# Punktwolke in Open3D laden
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(filtered_points_trans)
colors = np.tile([0.2, 0.6, 0.2], (len(filtered_points_trans), 1))
pcd.colors = o3d.utility.Vector3dVector(colors)

# Kugeln für Baumgipfel (nach E/N!)
sphere_list = []
for _, row in df.iterrows():
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=4)
    sphere.translate([row["E"], row["N"], row["Height_m"]])
    sphere.paint_uniform_color([1, 0.4, 0])  # orange
    sphere_list.append(sphere)

scene = [pcd] + sphere_list

# Bounding Box-Zentrum für Kamerapositionen
bbox = pcd.get_axis_aligned_bounding_box()
center = bbox.get_center()

# Bounding Box anzeigen (z. B. zur Orientierung)
bbox_lines = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(bbox)
bbox_lines.paint_uniform_color([0.5, 0.5, 0.5])  # grau
scene.append(bbox_lines)

# ---------- Screenshot 1: Draufsicht ----------
print("Screenshot: Draufsicht")
screenshot_top_path = os.path.join(output_dir, f"open3d_topdown_RunID_{RunID}.png")

vis = o3d.visualization.Visualizer()
try:
    vis.create_window(visible=True)
    for obj in scene:
        vis.add_geometry(obj)

    vc = vis.get_view_control()
    cam_params = vc.convert_to_pinhole_camera_parameters()
    cam_params.extrinsic = np.array([
        [1, 0, 0, center[0]],
        [0, -1, 0, center[1]],
        [0, 0, -1, center[2] + 600],
        [0, 0, 0, 1]
    ])
    vc.convert_from_pinhole_camera_parameters(cam_params)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(screenshot_top_path)
    print(f"Draufsicht gespeichert: {screenshot_top_path}")
finally:
    vis.destroy_window()

# ---------- Screenshot 2: Isometrische Ansicht ----------
print("Screenshot: Isometrische Ansicht")
screenshot_iso_path = os.path.join(output_dir, f"open3d_iso_RunID_{RunID}.png")

vis = o3d.visualization.Visualizer()
try:
    vis.create_window(visible=True)
    for obj in scene:
        vis.add_geometry(obj)

    vc = vis.get_view_control()
    cam_params = vc.convert_to_pinhole_camera_parameters()
    cam_params.extrinsic = np.array([
        [0.707, -0.707, 0, center[0] - 600],
        [0.5, 0.5, -0.707, center[1] - 600],
        [-0.5, -0.5, -0.707, center[2] + 400],
        [0, 0, 0, 1]
    ])
    vc.convert_from_pinhole_camera_parameters(cam_params)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(screenshot_iso_path)
    print(f"Isometrie gespeichert: {screenshot_iso_path}")
finally:
    vis.destroy_window()

# ---------- Optional: Interaktive Anzeige ----------
print("Öffne interaktives Open3D-Fenster ...")
o3d.visualization.draw_geometries(scene, window_name="3D: Bäume + Zentren")