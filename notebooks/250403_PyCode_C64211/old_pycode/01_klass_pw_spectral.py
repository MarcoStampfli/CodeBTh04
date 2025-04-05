import pandas as pd
import numpy as np
import os
from sklearn.cluster import SpectralClustering
import matplotlib.pyplot as plt
# import open3d as o3d

# Datei mit bereits berechneten HSV-Werten laden
file_path = "PW_KOO_RGB_HSV_norm.txt"  # Falls der Name anders ist, bitte anpassen
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen basierend auf der erweiterten Datei setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# Anzahl der Cluster definieren (zwischen 6 und 10)
num_clusters = 5  # Kann auf 6-10 angepasst werden

# Spectral Clustering auf HSV-Werte anwenden
spectral = SpectralClustering(n_clusters=num_clusters, affinity='nearest_neighbors', n_neighbors=10, random_state=42)
df["Color Cluster"] = spectral.fit_predict(df[["Hue (°)", "Saturation (%)", "Value (%)"]])

# Neue Datei speichern (mit Farbklassen, ohne Header)
output_path = "PW_5_Klassen_spectral.txt"
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

print(f"Datei mit Farbklassen gespeichert als: {output_path}")

# Erstelle einen Ordner für die Ausgabe (falls nicht vorhanden)
output_folder = "Spectral_Clustered_Files"
os.makedirs(output_folder, exist_ok=True)

# Daten in separate Dateien je Klasse speichern
for cluster_id in df["Color Cluster"].unique():
    # Filtere die Punkte für die aktuelle Klasse
    cluster_df = df[df["Color Cluster"] == cluster_id]
    
    # Dateiname für die Klasse
    output_file = os.path.join(output_folder, f"PW_Klasse_{int(cluster_id)}_spectral.txt")
    
    # Speichern ohne Header
    cluster_df.to_csv(output_file, sep=";", index=False, decimal=".", header=False)

    print(f"Datei gespeichert: {output_file}")

print("Alle Cluster-Dateien wurden erfolgreich erstellt!")

# # Datei zur Anzeige bringen
# import ace_tools as tools
# tools.display_dataframe_to_user(name="Geklassifizierte Punktwolken-Daten", dataframe=df)

# # Open3D: Punktwolke mit Clustern visualisieren
# points = df[["X coordinate", "Y coordinate", "Z coordinate"]].to_numpy()
# colors = df["Color Cluster"].to_numpy() / num_clusters  # Normieren für Farben

# # Punktwolke für Open3D vorbereiten
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points)
# pcd.colors = o3d.utility.Vector3dVector(plt.cm.jet(colors)[:, :3])  # Farben aus Jet-Colormap

# # Punktwolke anzeigen
# o3d.visualization.draw_geometries([pcd], window_name="Geklassifizierte Punktwolke")

