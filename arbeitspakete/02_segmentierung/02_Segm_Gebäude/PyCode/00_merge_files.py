import pandas as pd
import os

output_folder = "KMeans_input"
input_file = "250331_KMeans_advance\KMeans_input\Input__PW_Klasse_13_kmeans.txt"
# Datei mit Clustern laden
# input_file = os.path.join(output_folder, input_file)
df_full = pd.read_csv(input_file, sep=";", decimal=".", header=None)

# Letzte Spalte enthält die Cluster-Zuweisung
cluster_col = df_full.shape[1] - 1

# Cluster 0 & 2 kombinieren
combined_0_2 = df_full[df_full[cluster_col].isin([0, 2])]
output_0_2 = os.path.join(output_folder, "cluster_0_2_combined.txt")
combined_0_2.to_csv(output_0_2, sep=";", index=False, header=False, decimal=".")

# Cluster 1 & 3 kombinieren
combined_1_3 = df_full[df_full[cluster_col].isin([1, 3])]
output_1_3 = os.path.join(output_folder, "cluster_1_3_combined.txt")
combined_1_3.to_csv(output_1_3, sep=";", index=False, header=False, decimal=".")

print("Cluster 0+2 und 1+3 wurden jeweils in eigenen Dateien gespeichert.")
