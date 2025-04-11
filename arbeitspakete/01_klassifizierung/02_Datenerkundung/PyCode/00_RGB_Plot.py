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
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# KDE-Plots für RGB-Werte
plt.figure(figsize=(10, 6))
sns.kdeplot(df["Red color (0-255)"], label="Rot", color="red", fill=True)
sns.kdeplot(df["Green color (0-255)"], label="Grün", color="green", fill=True)
sns.kdeplot(df["Blue color (0-255)"], label="Blau", color="blue", fill=True)

# Diagramm formatieren
plt.title("Dichteverteilung der RGB-Werte")
plt.xlabel("Farbwert (0-255)")
plt.ylabel("Dichte")
plt.legend()
file_path = os.path.join(output_folder, "Dichteverteilung_RGB.png")
plt.savefig(file_path, dpi=300)
plt.show()
