import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

# Datei laden
file_path = r"C:\Users\st1174360\Documents\BTh_04_Vis\SeabornPlots\PW_KOO_RGB_HSV_norm.txt"
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

output_folder = "Diagramme"
os.makedirs(output_folder, exist_ok=True)

# Spaltennamen setzen
df.columns = [
    "X coordinate", "Y coordinate", "Z coordinate",
    "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
    "X scan dir", "Y scan dir", "Z scan dir",
    "Hue (°)", "Saturation (%)", "Value (%)"
]

# Figure einrichten
plt.figure(figsize=(10, 6))

# KDE-Plots für RGB-Werte, dabei clip=(0,255) damit keine Kurven über den Rand hinaus laufen
sns.kdeplot(
    df["Red color (0-255)"],
    label="Rot",
    color="red",
    fill=True,
    clip=(0, 255)
)
sns.kdeplot(
    df["Green color (0-255)"],
    label="Grün",
    color="green",
    fill=True,
    clip=(0, 255)
)
sns.kdeplot(
    df["Blue color (0-255)"],
    label="Blau",
    color="blue",
    fill=True,
    clip=(0, 255)
)

# X-Achse genau von 0 bis 255, 0 direkt am Rand
plt.xlim(0, 255)
plt.margins(x=0)  # entfernt jegliches Padding an den Rändern

# Diagramm formatieren
plt.title("Dichteverteilung der RGB-Werte")
plt.xlabel("Farbwert (0–255)")
plt.ylabel("Dichte")
plt.legend()

# Speichern und Anzeigen
output_path = os.path.join(output_folder, "Dichteverteilung_RGB.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
