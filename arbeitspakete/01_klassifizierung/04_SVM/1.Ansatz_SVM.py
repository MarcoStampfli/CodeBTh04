import pandas as pd
import numpy as np
import glob
from sklearn.svm import SVC
import open3d as o3d

# -----------------------------------
# 1. Trainingsdaten aus mehreren Dateien laden
# -----------------------------------

all_dfs = []
for i in range(7):  # 7 Klassen, class_0.txt bis class_6.txt
    filename = f"class_{i}.txt"
    df = pd.read_csv(filename, sep=";", header=None)
    df["label"] = i  # Klasse hinzufügen
    all_dfs.append(df)

train_df = pd.concat(all_dfs, ignore_index=True)

# Spaltennamen zuweisen
train_df.columns = ["x", "y", "z", "r", "g", "b", "nx", "ny", "nz", "label"]

X_train = train_df[["x", "y", "z", "r", "g", "b", "nx", "ny", "nz"]]
y_train = train_df["label"]

# -----------------------------------
# 2. SVM trainieren
# -----------------------------------
model = SVC(kernel="rbf", C=10, gamma=0.1)
model.fit(X_train, y_train)

# -----------------------------------
# 3. Neue, unklassifizierte Punktwolke laden
# -----------------------------------
unclassified_df = pd.read_csv("unclassified.txt", sep=";", header=None)
unclassified_df.columns = ["x", "y", "z", "r", "g", "b", "nx", "ny", "nz"]

X_test = unclassified_df[["x", "y", "z", "r", "g", "b", "nx", "ny", "nz"]]
y_pred = model.predict(X_test)

# -----------------------------------
# 4. Ergebnis speichern
# -----------------------------------
unclassified_df["predicted_label"] = y_pred
unclassified_df.to_csv("classified_result.txt", sep=";", index=False)

# -----------------------------------
# 5. Optional: Visualisierung
# -----------------------------------
color_map = [
    [1, 0, 0], [0, 1, 0], [0, 0, 1], 
    [1, 1, 0], [1, 0, 1], [0, 1, 1], [0.5, 0.5, 0.5]
]
colors = np.array([color_map[label % len(color_map)] for label in y_pred])

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(X_test[["x", "y", "z"]].values)
pcd.colors = o3d.utility.Vector3dVector(colors)
o3d.visualization.draw_geometries([pcd])
