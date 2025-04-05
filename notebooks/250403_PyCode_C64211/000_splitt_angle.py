import pandas as pd
import numpy as np

# === EINSTELLUNGEN ===
input_file = "PW_KOO_RGB_norm.txt"
upright_thresh = 0.985 # Waagrechte Flächenabweichung
flat_thresh = 0.25 # Senkrechte Flächenabweichung
"""
Z       	Winkel zur XY-Ebene (°)	Bedeutung 
1.00	        0.00°	            exakt senkrecht / aufrecht
0.98	        11.46°	            fast senkrecht (aufrecht)
0.87	        29.50°	            leicht geneigt (schräg)
0.50	        60.00°	            stark geneigt (schräg)
0.30	        72.54°	            fast waagrecht (schräg)
0.20	        78.46°	            nahezu waagrecht
0.00	        90.00°	            exakt waagrecht
"""
# === DATEN EINLESEN ===
df = pd.read_csv(input_file, sep=";", header=None, decimal=".")

# === SPALTEN BENENNEN ===
df.columns = ["X", "Y", "Z", "R", "G", "B", "X scan dir", "Y scan dir", "Z scan dir"]

# === FUNKTIONEN ===
def classify_orientation(z_val, upright_thresh=0.85, flat_thresh=0.05):
    z_abs = abs(z_val)
    if z_abs >= upright_thresh:
        return "aufrecht"
    elif z_abs <= flat_thresh:
        return "waagrecht"
    else:
        return "schräg"

def angle_to_xy_plane(z_component):
    z_abs = abs(z_component)
    angle_rad = np.arccos(z_abs)
    angle_deg = np.degrees(angle_rad)
    return round(angle_deg, 2)



# === ORIENTIERUNG UND WINKEL BERECHNEN ===
df["Orientation"] = df["Z scan dir"].apply(lambda z: classify_orientation(z, upright_thresh, flat_thresh))
df["Winkel (°)"] = df["Z scan dir"].apply(angle_to_xy_plane)

# === DATEN AUFTEILEN ===
df_aufrecht = df[df["Orientation"] == "aufrecht"]
df_waagrecht = df[df["Orientation"] == "waagrecht"]
df_schraeg = df[df["Orientation"] == "schräg"]

print(df[["X", "Y", "Z", "R", "G", "B", "X scan dir", "Y scan dir", "Z scan dir", "Winkel (°)", "Orientation"]].head(100))

# === AUSGABE DER VERTEILUNG ===
print("Orientierungs-Verteilung:")
print(df["Orientation"].value_counts())
print("\nBeispielhafte Zeilen:")
print(df.head())

# === DATEIEN SPEICHERN ===
df_aufrecht.to_csv(f"punkte_aufrecht_{upright_thresh}.txt", sep=";", index=False, header=False, decimal=".")
df_waagrecht.to_csv(f"punkte_waagrecht_{flat_thresh}.txt", sep=";", index=False, header=False, decimal=".")
df_schraeg.to_csv(f"punkte_schraeg_{flat_thresh}_{upright_thresh}.txt", sep=";", index=False, header=False, decimal=".")

print("\nDateien wurden gespeichert:")
print(f"- aufrecht → punkte_aufrecht_{upright_thresh}.txt")
print(f"- waagrecht → punkte_waagrecht_{flat_thresh}.txt")
print(f"- schräg → punkte_schraeg_{flat_thresh}_{upright_thresh}.txt")