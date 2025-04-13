import pandas as pd

# Daten einlesen
df = pd.read_csv("PW_KOO_RGB_norm.txt", sep=";", header=None, decimal=".")

# Spalten zuweisen
df.columns = ["X", "Y", "Z", "R", "G", "B", "X scan dir", "Y scan dir", "Z scan dir"]

# Schwellenwerte
upright_thresh = 0.99
flat_thresh = 0.25

# Orientierung klassifizieren
def classify_orientation(z_val, upright_thresh=upright_thresh, flat_thresh=flat_thresh):
    z_abs = abs(z_val)
    if z_abs >= upright_thresh:
        return "waagrecht"
    elif z_abs <= flat_thresh:
        return "aufrecht"
    else:
        return "schräg"

# Neue Spalte: Orientation
df["Orientation"] = df["Z scan dir"].apply(lambda z: classify_orientation(z, upright_thresh, flat_thresh))

# Gruppen trennen
df_aufrecht = df[df["Orientation"] == "waagrecht"]
df_waagrecht = df[df["Orientation"] == "aufrecht"]
df_schräg = df[df["Orientation"] == "schräg"]

# Ausgabe
print(df["Orientation"].value_counts())

# Speichern
df_aufrecht.to_csv(f"punkte_waagrecht_{upright_thresh}.txt", sep=";", index=False, header=False, decimal=".")
df_waagrecht.to_csv(f"punkte_aufrecht_{flat_thresh}.txt", sep=";", index=False, header=False, decimal=".")
df_schräg.to_csv(f"punkte_schraeg_{flat_thresh}_{upright_thresh}.txt", sep=";", index=False, header=False, decimal=".")
