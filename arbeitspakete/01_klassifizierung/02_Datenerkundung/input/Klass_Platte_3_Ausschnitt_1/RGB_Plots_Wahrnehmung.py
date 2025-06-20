import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
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
        "X", "Y", "Z", "R", "G", "B",
        "Xscan", "Yscan", "Zscan",
        "Hue", "Saturation", "Value"
    ]
    rgb_mean = df[["R", "G", "B"]].mean()
    return (
        rgb_mean["R"] / 255.0,
        rgb_mean["G"] / 255.0,
        rgb_mean["B"] / 255.0
    )

def main():
    # 🔧 Pfade & Einstellungen
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    output_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\output"
    dateiname = "RGB_Mensch_Wissenschaft_Kacheln.png"
    os.makedirs(output_pfad, exist_ok=True)
    dateipfad = os.path.join(output_pfad, dateiname)
    sep = ";"

    # 📥 Daten laden
    dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
    if not dateien:
        raise FileNotFoundError(f"Keine .txt-Dateien in '{ordner_pfad}' gefunden.")

    klassen, mean_rgbs, grauwert_mensch, grauwert_wissenschaft = [], [], [], []

    for dateiname in dateien:
        klasse = get_klasse(dateiname)
        path = os.path.join(ordner_pfad, dateiname)
        rgb = lade_mittel_rgb(path, sep=sep)

        klassen.append(klasse)
        mean_rgbs.append(rgb)
        grauwert_mensch.append(berechne_grauwert_menschlich(rgb))
        grauwert_wissenschaft.append(berechne_grauwert_wissenschaftlich(rgb))

    # 📊 Plot: 3 Zeilen (RGB, Mensch, Wissenschaft), n+1 Spalten (inkl. linker Beschriftung)
    n = len(klassen)
    zeilen_labels = ["RGB", "Mensch", "Wissenschaft"]
    farben_matrix = [mean_rgbs, grauwert_mensch, grauwert_wissenschaft]

    fig, axes = plt.subplots(nrows=3, ncols=n+1, figsize=((n + 1) * 2, 6),
                             gridspec_kw={'hspace': 0.1, 'wspace': 0})

    # Plot befüllen
    for row in range(3):
        for col in range(n + 1):
            ax = axes[row][col]
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            if col == 0:
                # Linke Beschriftung
                ax.set_facecolor("white")
                ax.text(0.5, 0.5, zeilen_labels[row],
                        transform=ax.transAxes, ha='center', va='center',
                        fontsize=11, fontweight='bold')
            else:
                # Farbfläche
                ax.set_facecolor(farben_matrix[row][col - 1])
                if row == 0:
                    ax.set_title(klassen[col - 1], fontsize=11, fontweight='bold')

    # Speichern
    fig.suptitle("Farb- & Grauwahrnehmung: RGB – Mensch – Wissenschaft", fontsize=14, y=1.03)
    plt.tight_layout()
    fig.savefig(dateipfad, dpi=300, bbox_inches='tight')
    print(f"✅ Grafik gespeichert unter: {dateipfad}")

if __name__ == "__main__":
    main()
