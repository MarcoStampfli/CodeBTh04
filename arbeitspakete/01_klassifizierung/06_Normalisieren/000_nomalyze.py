import pandas as pd
import numpy as np
import colorsys
from pathlib import Path

# === EINSTELLUNGEN ===
input_file = Path(r"arbeitspakete\01_klassifizierung\06_Normalisieren\input\P3A1_Gebaeude.txt")
# input_folder = Path("250331_KMeans_advance\KMeans_input")  # Ordner mit den TXT-Dateien
output_folder = Path("./output")  # Zielordner für die normalisierten Dateien
# input_folder = Path("./input")  # Ordner mit den TXT-Dateien
# output_folder = Path("./output")  # Zielordner für die normalisierten Dateien
output_folder.mkdir(exist_ok=True)

# # === ALLE .txt-DATEIEN IM ORDNER VERARBEITEN ===
# for input_file in input_folder.glob("*.txt"):
df = pd.read_csv(input_file, sep=";", header=None, decimal=".")

# === SPALTEN BENENNEN ===
df.columns = [
    "X coordinate", "Y coordinate", "Z coordinate",
    "Red", "Green", "Blue",
    "X scan dir", "Y scan dir", "Z scan dir"
]

# === RGB Normalisieren (schnell via Vektorisierung) ===
df["Red (0-1)"] = df["Red"] / 255.0
df["Green (0-1)"] = df["Green"] / 255.0
df["Blue (0-1)"] = df["Blue"] / 255.0

# === RGB → HSV Umrechnen (schnell mit NumPy + List Comprehension) ===
rgb_array = df[["Red (0-1)", "Green (0-1)", "Blue (0-1)"]].to_numpy()
hsv_array = np.array([colorsys.rgb_to_hsv(r, g, b) for r, g, b in rgb_array])
df[["Hue (0-1)", "Saturation (0-1)", "Value (0-1)"]] = hsv_array

# === SPALTEN IN GEWÜNSCHTER REIHENFOLGE ANORDNEN ===
df = df[[
    "X coordinate", "Y coordinate", "Z coordinate",
    "Red (0-1)", "Green (0-1)", "Blue (0-1)",
    "Hue (0-1)", "Saturation (0-1)", "Value (0-1)",
    "X scan dir", "Y scan dir", "Z scan dir"
]]

# === AUSGABEDATEI SPEICHERN ===
output_file = output_folder / f"{input_file.stem}_normalisiert.txt"
df.to_csv(output_file, sep=";", index=False, header=False, decimal=".")

print(f"✔ {input_file.name} → gespeichert als {output_file.name}")
