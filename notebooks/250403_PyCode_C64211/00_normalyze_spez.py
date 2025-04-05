import pandas as pd
import colorsys
from pathlib import Path

# === EINSTELLUNGEN ===
input_folder = Path("./Klass_Platte_3_Ausschnitt_1")  # Ordner mit den TXT-Dateien
output_folder = Path("./output")  # Zielordner für die normalisierten Dateien
output_folder.mkdir(exist_ok=True)

# === RGB Normalisieren ===
def rgb_normalize(row):
    r, g, b = row["Red"], row["Green"], row["Blue"]
    return pd.Series([r / 255.0, g / 255.0, b / 255.0])

# === RGB → HSV umrechnen ===
def rgb_to_hsv(row):
    r, g, b = row["Red"] / 255.0, row["Green"] / 255.0, row["Blue"] / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return pd.Series([h, s, v])

# === ALLE .txt-DATEIEN IM ORDNER VERARBEITEN ===
for input_file in input_folder.glob("*.txt"):
    df = pd.read_csv(input_file, sep=";", header=None, decimal=".")
    file_name = input_file.stem
    klass = file_name.split(sep="_")[-1]

    # === SPALTEN BENENNEN ===
    df.columns = [
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red", "Green", "Blue",
        "X scan dir", "Y scan dir", "Z scan dir"
    ]

    # === Neue Spalten berechnen ===
    df[["Red (0-1)", "Green (0-1)", "Blue (0-1)"]] = df.apply(rgb_normalize, axis=1)
    df[["Hue (0-1)", "Saturation (0-1)", "Value (0-1)"]] = df.apply(rgb_to_hsv, axis=1)

    # === SPALTEN IN GEWÜNSCHTER REIHENFOLGE ANORDNEN ===
    df = df[[
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red (0-1)", "Green (0-1)", "Blue (0-1)",
        "Hue (0-1)", "Saturation (0-1)", "Value (0-1)",
        "X scan dir", "Y scan dir", "Z scan dir"
    ]]

    # === AUSGABEDATEI SPEICHERN ===
    output_file = output_folder / f"PW_Klass_P3A1_{klass}_normalisiert.txt"
    df.to_csv(output_file, sep=";", index=False, header=False, decimal=".")

    print(f"✔ {input_file.name} → gespeichert als {output_file.name}")
