import pandas as pd
import colorsys

# Datei einlesen (Semikolon-getrennt, ohne Header)
file_path = r"SeabornPlots\Platte_3_Ausschnitt_3.txt"  # Ersetze mit deinem Dateipfad
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen manuell zuweisen (basierend auf deinem Screenshot)
df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
              "X scan dir", "Y scan dir", "Z scan dir"]

# RGB in HSV umrechnen
def rgb_to_hsv(row):
    r, g, b = row["Red color (0-255)"], row["Green color (0-255)"], row["Blue color (0-255)"]
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)  # Normalisierung (0-1 Bereich)
    return pd.Series([h*360, s*100, v*100])  # H in Grad (0-360), S/V in Prozent (0-100)

# HSV berechnen und zur Tabelle hinzufügen
df[["Hue (°)", "Saturation (%)", "Value (%)"]] = df.apply(rgb_to_hsv, axis=1)

# Neue Datei speichern (ohne Header)
output_path = "P3A3_KOO_RGB_HSV_norm.txt"
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)

print(f"Datei wurde erweitert und gespeichert als: {output_path}")

# Datei zur Anzeige bringen
# import ace_tools as tools
# tools.display_dataframe_to_user(name="Erweiterte Punktwolken-Daten", dataframe=df)

