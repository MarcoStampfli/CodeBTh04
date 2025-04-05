import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

# Datei laden
file_path = r"PW_KOO_RGB_HSV_norm.txt"
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# Zufällige 1000 Zeilen für bessere Performance
df_sample = df.sample(1000, random_state=42) # Teildatensatz
df_sample = df

# Ordner für Diagramme erstellen (falls nicht vorhanden)
output_folder = "Diagramme"
os.makedirs(output_folder, exist_ok=True)

# --- Red vs. Green ---
plt.figure(figsize=(8, 6))
sns.kdeplot(
    x=df_sample["Red color (0-255)"], 
    y=df_sample["Green color (0-255)"], 
    cmap="coolwarm", fill=True
)
plt.xlabel("Red (0-255)")
plt.ylabel("Green (0-255)")
plt.title("2D KDE: Red vs. Green")
file_path = os.path.join(output_folder, "KDE_Red_vs_Green.png")
plt.savefig(file_path, dpi=300)
plt.show()

# --- Red vs. Blue ---
plt.figure(figsize=(8, 6))
sns.kdeplot(
    x=df_sample["Red color (0-255)"], 
    y=df_sample["Blue color (0-255)"], 
    cmap="coolwarm", fill=True
)
plt.xlabel("Red (0-255)")
plt.ylabel("Blue (0-255)")
plt.title("2D KDE: Red vs. Blue")
file_path = os.path.join(output_folder, "KDE_Red_vs_Blue.png")
plt.savefig(file_path, dpi=300)
plt.show()

# --- Green vs. Blue ---
plt.figure(figsize=(8, 6))
sns.kdeplot(
    x=df_sample["Green color (0-255)"], 
    y=df_sample["Blue color (0-255)"], 
    cmap="coolwarm", fill=True
)
plt.xlabel("Green (0-255)")
plt.ylabel("Blue (0-255)")
plt.title("2D KDE: Green vs. Blue")
file_path = os.path.join(output_folder, "KDE_Green_vs_Blue.png")
plt.savefig(file_path, dpi=300)
plt.show()

print(f"Alle RGB-Plots wurden im Ordner '{output_folder}' gespeichert!")
