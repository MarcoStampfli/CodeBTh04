import pandas as pd
import colorsys
import numpy as np
import time

# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================

start_total = time.time()

# Datei einlesen (Semikolon-getrennt, ohne Header)
file_path = "250331_KMeans_Klass\\KMeans_input\\Input__PW_Klasse_13_kmeans.txt"  # ← ggf. anpassen
start_read = time.time()
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)
end_read = time.time()

# Spaltennamen manuell zuweisen
df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
              "X scan dir", "Y scan dir", "Z scan dir", "Klasse"]

# RGB normalisieren (0–1)
start_rgb = time.time()
df["R_norm"] = df["Red color (0-255)"] / 255.0
df["G_norm"] = df["Green color (0-255)"] / 255.0
df["B_norm"] = df["Blue color (0-255)"] / 255.0
end_rgb = time.time()

# RGB → HSV (vektorisiert)
start_hsv = time.time()
rgb_norm = df[["R_norm", "G_norm", "B_norm"]].to_numpy()
hsv = np.apply_along_axis(lambda x: colorsys.rgb_to_hsv(*x), 1, rgb_norm)
df[["Hue_norm", "Saturation_norm", "Value_norm"]] = pd.DataFrame(hsv, index=df.index)
end_hsv = time.time()

# Spalten in gewünschter Reihenfolge anordnen
df = df[[ 
    "X coordinate", "Y coordinate", "Z coordinate",
    "R_norm", "G_norm", "B_norm",
    "Hue_norm", "Saturation_norm", "Value_norm",
    "X scan dir", "Y scan dir", "Z scan dir", "Klasse"
]]

# Datei speichern
start_save = time.time()
output_path = "02_PW_KOO_RGB_HSV_normiert_0_1.txt"
df.to_csv(output_path, sep=";", index=False, decimal=".", header=False)
end_save = time.time()

end_total = time.time()

# Zeit-Report
print(f"\n✅ Verarbeitung abgeschlossen.")
print(f"📥 Einlesen der Datei:       {end_read - start_read:.2f} Sek.")
print(f"🎨 RGB-Normalisierung:      {end_rgb - start_rgb:.2f} Sek.")
print(f"🌈 HSV-Umrechnung:          {end_hsv - start_hsv:.2f} Sek.")
print(f"💾 Speichern der Datei:     {end_save - start_save:.2f} Sek.")
print(f"⏱️ Gesamtlaufzeit:           {end_total - start_total:.2f} Sek.")
