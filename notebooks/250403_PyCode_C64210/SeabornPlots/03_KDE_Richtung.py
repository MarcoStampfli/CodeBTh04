import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import time


start = time.time()
# Datei laden
file_path = r"SeabornPlots\PW_KOO_RGB_HSV_norm.txt"
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen setzen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# Zufällige 1000 Zeilen für bessere Performance
# df_sample = df.sample(1000, random_state=42) #Teildatensatz
df_sample = df #Ganzerdatensatz

# Ordner für Diagramme erstellen (falls nicht vorhanden)
output_folder = "Diagramme"
os.makedirs(output_folder, exist_ok=True)

# --- Red vs. Z Komponente ---
plt.figure(figsize=(8, 6))
sns.kdeplot(
    x=df_sample["Z scan dir"], 
    y=df_sample["Red color (0-255)"], 
    cmap="coolwarm", fill=True
)
plt.xlabel("Z-Komponente (0-1)")
plt.ylabel("Red color (0-255)")
plt.title("2D KDE: Z-Komponente vs. Rot")
file_path = os.path.join(output_folder, "KDE_Znorm_vs_Red.png")
plt.savefig(file_path, dpi=300)

end_time = time.time()
elapsed_time = end_time - start
minutes = int(elapsed_time // 60)
seconds = elapsed_time % 60
print(f"Gesamtlaufzeit: {minutes} Minuten und {seconds:.2f} Sekunden")

plt.show()


