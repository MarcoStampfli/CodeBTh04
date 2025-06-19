import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def berechne_grauwert_wissenschaftlich(rgb: tuple) -> tuple:
    r_lin = srgb_to_linear(rgb[0])
    g_lin = srgb_to_linear(rgb[1])
    b_lin = srgb_to_linear(rgb[2])
    gray = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    return (gray, gray, gray)

def berechne_grauwert_menschlich(rgb: tuple) -> tuple:
    gray = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return (gray, gray, gray)

def get_klasse(dateiname: str) -> str:
    basis = dateiname.replace("_HSV.txt", "")
    return basis.split("_")[-1]

def lade_mittel_rgb(dateipfad: str, sep: str = ";") -> tuple:
    df = pd.read_csv(dateipfad, sep=sep, decimal=".", header=None)
    if df.shape[1] != 12:
        raise ValueError(f"Datei '{os.path.basename(dateipfad)}' liefert {df.shape[1]} Spalten statt 12.")
    df.columns = [
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
        "X scan dir", "Y scan dir", "Z scan dir",
        "Hue (°)", "Saturation (%)", "Value (%)"
    ]
    rgb_mean = df[["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)"]].mean()
    return (
        rgb_mean["Red color (0-255)"] / 255.0,
        rgb_mean["Green color (0-255)"] / 255.0,
        rgb_mean["Blue color (0-255)"] / 255.0
    )

def erstelle_kachelreihe(farben, klassen, titel, dateipfad):
    n = len(klassen)
    tile_size = 2
    fig, axes = plt.subplots(nrows=1, ncols=n,
                             figsize=(n * tile_size, tile_size),
                             constrained_layout=True)

    if n == 1:
        axes = [axes]

    for ax, farbe, klasse in zip(axes, farben, klassen):
        ax.set_facecolor(farbe)
        ax.set_aspect('equal')
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(klasse, fontsize=10)

    fig.suptitle(titel, fontsize=12, y=1.08)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.85, bottom=0.01, wspace=0)
    fig.savefig(dateipfad, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✅ Gespeichert: {dateipfad}")

def main():
    # 🔧 Pfade
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    output_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\output"
    os.makedirs(output_pfad, exist_ok=True)

    # 📥 Daten
    dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
    if not dateien:
        raise FileNotFoundError(f"Keine .txt-Dateien in '{ordner_pfad}' gefunden.")

    klassen, mean_rgbs, grau_mensch, grau_wissenschaft = [], [], [], []

    for file in dateien:
        klasse = get_klasse(file)
        pfad = os.path.join(ordner_pfad, file)
        rgb = lade_mittel_rgb(pfad)

        klassen.append(klasse)
        mean_rgbs.append(rgb)
        grau_mensch.append(berechne_grauwert_menschlich(rgb))
        grau_wissenschaft.append(berechne_grauwert_wissenschaftlich(rgb))

    # 🖼 Export
    erstelle_kachelreihe(mean_rgbs, klassen, "RGB-Mittelwerte pro Klasse",
                         os.path.join(output_pfad, "Doku_rgb_kacheln.png"))
    
    erstelle_kachelreihe(grau_mensch, klassen, "Grauwert pro Klasse",
                         os.path.join(output_pfad, "Doku_grauwert_kacheln.png"))
    
    # erstelle_kachelreihe(grau_wissenschaft, klassen, "Grauwert nach wissenschaftlichem Modell (Rec.709)",
    #                      os.path.join(output_pfad, "Doku_grau_wissenschaft_kacheln.png"))

if __name__ == "__main__":
    main()
