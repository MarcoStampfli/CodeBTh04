import pandas as pd
import numpy as np
import os
import time
from tqdm import tqdm

import matplotlib.pyplot as plt
# import open3d as o3d

from sklearn.cluster import KMeans

# Datei laden
file_path = "250327_Normalisieren\output\PW_P3_normalisiert.txt"
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen Datei setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
            "Red (0-1)", "Green (0-1)", "Blue (0-1)",
            "Hue (0-1)", "Saturation (0-1)", "Value (0-1)",
            "X scan dir", "Y scan dir", "Z scan dir"]

# Anzahl der Cluster definieren
num_clusters = 3  # Anzahl Zielklassen für Output
fit = df[["Hue (0-1)"]] # Fit Variablen

# K-Means
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
df["Color Cluster"] = kmeans.fit_predict(fit)

# Speichern der einzelnen Cluster-Dateien
...
