import pandas as pd
import colorsys

# Datei einlesen (Semikolon-getrennt, ohne Header)
file_path = "250331_KMeans_advance\\KMeans_input\\Input__PW_Klasse_13_kmeans.txt"  # ← ggf. anpassen
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen manuell zuweisen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
              "X scan dir", "Y scan dir", "Z scan dir", "Klasse"]

# RGB normalisieren (0–1)
df["R_norm"] = df["Red color (0-255)"] / 255.0
df["G_norm"] = df["Green color (0-255)"] / 255.0
df["B_norm"] = df["Blue color (0-255)"] / 255.0

# RGB → HSV (normiert)
def rgb_to_hsv(row):
    h, s, v = colorsys.rgb_to_hsv(row["R_norm"], row["G_norm"], row["B_norm"])
    return pd.Series([h, s, v])  # alles im Bereich 0–1

df[["Hue_norm", "Saturation_norm", "Value_norm"]] = df.apply(rgb_to_hsv, axis=1)

# Spalten in gewünschter Reihenfolge anordnen
df = df[[
    "X coordinate", "Y coordinate", "Z coordinate",
    "R_norm", "G_norm", "B_norm",
    "Hue_norm", "Saturation_norm", "Value_norm",
    "X scan dir", "Y scan dir", "Z scan dir", "Klasse"
]]

# Datei speichern
output_path = "13_PW_KOO_RGB_HSV_normiert_0_1.txt"
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

print(f"Normierte RGB+HSV-Werte wurden gespeichert als: {output_path}")



# Datei zur Anzeige bringen
# import ace_tools as tools
# tools.display_dataframe_to_user(name="Erweiterte Punktwolken-Daten", dataframe=df)

