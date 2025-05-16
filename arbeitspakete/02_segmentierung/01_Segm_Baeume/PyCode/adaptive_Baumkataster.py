import laspy
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull

# Punktwolke laden
las = laspy.read("deine_punktwolke.las")
points = np.vstack((las.x, las.y, las.z)).T
vegetation = points[points[:, 2] > 2.0]  # nur Vegetation

# Klasseneinteilung nach Höhe
bins = [2, 8, 14, 20, 100]  # z.B. <8m, 8–14m, 14–20m, >20m
eps_values = [1.0, 1.5, 2.0, 2.5]  # für jede Klasse ein eps

tree_data = []
label_offset = 0  # damit die Tree_IDs global eindeutig bleiben

for i in range(len(bins) - 1):
    z_min, z_max = bins[i], bins[i + 1]
    eps = eps_values[i]

    class_points = vegetation[(vegetation[:, 2] >= z_min) & (vegetation[:, 2] < z_max)]
    if len(class_points) == 0:
        continue

    # DBSCAN auf diese Höhenklasse
    db = DBSCAN(eps=eps, min_samples=30)
    labels = db.fit_predict(class_points)

    for label in np.unique(labels):
        if label == -1:
            continue
        cluster = class_points[labels == label]

        # Höhe
        height = cluster[:, 2].max() - cluster[:, 2].min()
        hull = ConvexHull(cluster[:, :2])
        diameter = np.sqrt(4 * hull.area / np.pi)
        centroid = np.mean(cluster, axis=0)

        tree_data.append({
            "Tree_ID": label + label_offset,
            "X": centroid[0],
            "Y": centroid[1],
            "Z": centroid[2],
            "Height_m": height,
            "Crown_Diameter_m": diameter
        })

    label_offset += labels.max() + 1  # für globale Tree_IDs

# Ausgabe
df = pd.DataFrame(tree_data)
df.to_csv("adaptive_baumcluster.csv", index=False)
print(df.head())
