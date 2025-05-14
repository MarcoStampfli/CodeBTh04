import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Pfad zur normalisierten Punktwolke (HSV-Daten)
file_path = r"250327_Normalisieren\output\PW_P3_normalisiert.txt"
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
k_values = np.arange(1, 9)
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df[["Hue (0-1)"]])
    wcss.append(kmeans.inertia_)

# 3. Hyperbel-Referenz (Startwert WCSS_1 geteilt durch k)
hyperbola = wcss[0] / k_values

# 4. Elbow-Punkt automatisch bestimmen
# Gerade durch den ersten und letzten Punkt
p1 = np.array([k_values[0], wcss[0]])
p2 = np.array([k_values[-1], wcss[-1]])

# Funktion: Abstand Punkt ↔ Gerade
def distance_to_line(pt, p1, p2):
    return abs(np.cross(p2 - p1, p1 - pt)) / np.linalg.norm(p2 - p1)

# Abstände berechnen
distances = np.array([distance_to_line(np.array([k, s]), p1, p2)
                      for k, s in zip(k_values, wcss)])
elbow_idx = distances.argmax()
elbow_k = k_values[elbow_idx]
elbow_wcss = wcss[elbow_idx]

# 5. Plot erstellen
plt.figure(figsize=(8, 5))
plt.plot(k_values, wcss, 'o-', label="WCSS (Elbow-Methode)", linewidth=2)
plt.plot(k_values, hyperbola, 's--', label="Referenz: Hyperbel (1/x Skala)", linewidth=2)

# Knick als roter Punkt markieren
plt.scatter(elbow_k, elbow_wcss, color='red', s=100, label=f'Elbow @ k={elbow_k}')

# Beschriftung des Punkts
plt.annotate(
    f'Elbow: k={elbow_k}',
    xy=(elbow_k, elbow_wcss),
    xytext=(elbow_k + 0.5, elbow_wcss + (max(wcss) * 0.05)),
    arrowprops=dict(arrowstyle='->', color='red')
)

# Achsen & Titel
plt.xticks(k_values)
plt.xlabel("Anzahl der Cluster k")
plt.ylabel("Within-Cluster Sum of Squares (WCSS)")
plt.title("Elbow-Methode: WCSS vs. Clusteranzahl")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
