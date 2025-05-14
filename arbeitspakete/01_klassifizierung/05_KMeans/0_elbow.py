import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Pfad zur normalisierten Punktwolke (HSV-Daten)
file_path = r"C:\Users\st1174360\Documents\BTh_04\250327_Normalisieren\output\PW_P3A1_normalisiert.txt"  # ggf. anpassen

# 1. Daten einlesen
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)
df.columns = [
    "X coordinate", "Y coordinate", "Z coordinate",
    "Red (0-1)", "Green (0-1)", "Blue (0-1)",
    "Hue (0-1)", "Saturation (0-1)", "Value (0-1)",
    "X scan dir", "Y scan dir", "Z scan dir"
]

# 2. WCSS für k = 1 bis 12 berechnen
wcss = []
k_values = range(1, 13)
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df[["Hue (0-1)"]])
    wcss.append(kmeans.inertia_)

# 3. Hyperbel-Referenz (Startwert WCSS_1 geteilt durch k)
hyperbola = [wcss[0] / k for k in k_values]

# 4. Plot erstellen
plt.figure(figsize=(8, 5))
plt.plot(k_values, wcss, 'o-', label="WCSS (Elbow-Methode)", linewidth=2)
plt.plot(k_values, hyperbola, 's--', label="Referenz: Hyperbel (1/x Skala)", linewidth=2)
plt.xticks(k_values)
plt.xlabel("Anzahl der Cluster k")
plt.ylabel("Within-Cluster Sum of Squares (WCSS)")
plt.title("Elbow-Methode: WCSS vs. Clusteranzahl")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
