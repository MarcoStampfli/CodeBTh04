import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
    # Wunsch-Reihenfolge der Klassen (jeweils 4 pro Zeile)
    wunsch_reihenfolge = [
        "Bäume", "Fassade", "Flachdach", "Schrägdach",
        "Grünflächen", "Strasse", "Trottoir", "Wasser"
    ]
    kacheln_pro_zeile = 4
    n_zeilen = 2

    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    sep = ";"
    output_png = "RGB_Kacheln_pro_Klasse_sortiert.png"

    # Einlesen
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

    # Nach Wunschreihenfolge sortieren
    klasse2rgb = {klasse: rgb for klasse, rgb in zip(klassen, mean_rgbs)}
    klassen_geordnet = []
    mean_rgbs_geordnet = []
    for klasse in wunsch_reihenfolge:
        if klasse in klasse2rgb:
            klassen_geordnet.append(klasse)
            mean_rgbs_geordnet.append(klasse2rgb[klasse])
        else:
            print(f"Warnung: Klasse '{klasse}' nicht gefunden und wird übersprungen!")

    # Plot: 2 Zeilen, 4 Spalten
    fig, axes = plt.subplots(
        nrows=n_zeilen,
        ncols=kacheln_pro_zeile,
        figsize=(kacheln_pro_zeile * 2.5, n_zeilen * 2.2),
        gridspec_kw={'wspace': 0.1, 'hspace': 0.1}
    )

    axes = np.array(axes)  # für Einheitlichkeit

    # Kacheln einfärben & Klasse beschriften
    for idx, (klasse, rgb) in enumerate(zip(klassen_geordnet, mean_rgbs_geordnet)):
        zeile = idx // kacheln_pro_zeile
        spalte = idx % kacheln_pro_zeile
        ax = axes[zeile, spalte]
        ax.set_facecolor(rgb)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Beschriftung: Obere Zeile -> oben, untere Zeile -> unten
        if zeile == 0:
            # Oben
            ax.text(
                0.5, 1.05, klasse,  # y=1.05 ist knapp oberhalb der Kachel
                transform=ax.transAxes,
                ha='center', va='bottom',
                fontsize=14, fontweight='bold'
            )
        else:
            # Unten
            ax.text(
                0.5, -0.05, klasse,  # y=-0.05 ist knapp unterhalb der Kachel
                transform=ax.transAxes,
                ha='center', va='top',
                fontsize=14, fontweight='bold'
            )

    # Leere Felder ausblenden (falls weniger als 8 Klassen)
    for idx in range(len(klassen_geordnet), n_zeilen * kacheln_pro_zeile):
        zeile = idx // kacheln_pro_zeile
        spalte = idx % kacheln_pro_zeile
        axes[zeile, spalte].axis('off')

    fig.suptitle("Durchschnittliche RGB-Farben pro Klasse", fontsize=16, y=1.04)
    plt.tight_layout()
    fig.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"Die Grafik wurde gespeichert als '{output_png}'")
    # plt.show()

if __name__ == "__main__":
    main()
