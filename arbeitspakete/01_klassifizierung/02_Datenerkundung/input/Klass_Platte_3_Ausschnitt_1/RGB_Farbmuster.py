import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

def get_klasse(dateiname: str) -> str:
    basis = dateiname.replace("_HSV.txt", "")
    return basis.split("_")[-1]

def lade_mittel_rgb(dateipfad: str, sep: str = ";") -> tuple:
    df = pd.read_csv(dateipfad, sep=sep, decimal=".", header=None)
    if df.shape[1] != 12:
        raise ValueError(
            f"Datei '{os.path.basename(dateipfad)}' liefert {df.shape[1]} Spalten statt 12."
        )
    df.columns = [
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
        "X scan dir", "Y scan dir", "Z scan dir",
        "Hue (°)", "Saturation (%)", "Value (%)"
    ]
    rgb_mean = df[["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)"]].mean()
    mean_rgb = (
        rgb_mean["Red color (0-255)"] / 255.0,
        rgb_mean["Green color (0-255)"] / 255.0,
        rgb_mean["Blue color (0-255)"] / 255.0
    )
    return mean_rgb

def main():
    # ------------------------------
    # 1) Einstellungen: Pfade und Parameter
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    sep = ";"
    output_png = "RGB_Kacheln_pro_Klasse_2row.png"

    # ------------------------------
    # 2) Einlesen der Dateinamen und Berechnung der Mittel-RGB-Werte
    dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
    if len(dateien) == 0:
        raise FileNotFoundError(f"Keine .txt-Dateien gefunden in '{ordner_pfad}'")

    klassen = []
    mean_rgbs = []

    for dateiname in dateien:
        klasse = get_klasse(dateiname)
        dateipfad = os.path.join(ordner_pfad, dateiname)
        mean_rgb = lade_mittel_rgb(dateipfad, sep=sep)
        klassen.append(klasse)
        mean_rgbs.append(mean_rgb)

    # ------------------------------
    # 3) Plot-Vorbereitung: 4 Kacheln pro Zeile
    n = len(klassen)
    kacheln_pro_zeile = 4
    n_zeilen = math.ceil(n / kacheln_pro_zeile)

    fig, axes = plt.subplots(
        nrows=n_zeilen,
        ncols=kacheln_pro_zeile,
        figsize=(kacheln_pro_zeile * 2.2, n_zeilen * 2.2),     # Größe pro Kachel
        gridspec_kw={'wspace': 0.1, 'hspace': 0.2}
    )

    # Bei nur einer Zeile axes zu 2D-Liste machen
    if n_zeilen == 1:
        axes = np.array([axes])

    # ------------------------------
    # 4) Für jede Klasse eine Kachel einfärben und Namen darunter schreiben
    for idx, (klasse, rgb) in enumerate(zip(klassen, mean_rgbs)):
        zeile = idx // kacheln_pro_zeile
        spalte = idx % kacheln_pro_zeile
        ax = axes[zeile, spalte]
        ax.set_facecolor(rgb)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(
            0.5, -0.05, klasse,
            transform=ax.transAxes,
            ha='center', va='top',
            fontsize=14, fontweight='bold'
        )

    # Überzählige leere Achsen ausblenden (wenn z.B. 7 Klassen → 1 leeres Feld)
    for idx in range(n, n_zeilen * kacheln_pro_zeile):
        zeile = idx // kacheln_pro_zeile
        spalte = idx % kacheln_pro_zeile
        axes[zeile, spalte].axis('off')

    # ------------------------------
    # 5) Gesamt-Titel und Speicherung
    fig.suptitle("Durchschnittliche RGB-Farben pro Klasse", fontsize=18, y=1.02)
    plt.tight_layout()
    fig.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"Die Grafik wurde gespeichert als '{output_png}'")

if __name__ == "__main__":
    main()
