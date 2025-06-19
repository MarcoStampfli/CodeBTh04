import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_klasse(dateiname: str) -> str:
    """
    Extrahiert den Klassennamen aus dem Dateinamen.
    Beispiel:
        "XYZ_Bäume_HSV.txt" → "Bäume"
    """
    basis = dateiname.replace("_HSV.txt", "")
    return basis.split("_")[-1]

def lade_mittel_rgb(dateipfad: str, sep: str = ";") -> tuple:
    """
    Liest eine HSV-Datei ein und gibt den normalisierten RGB-Mittelwert zurück.
    Erwartet beim Einlesen 12 Spalten:
      [X, Y, Z, R, G, B, Xscan, Yscan, Zscan, Hue, Saturation, Value]
    """
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
    # Durchschnitt der RGB-Werte und Normierung auf [0..1]
    rgb_mean = df[["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)"]].mean()
    mean_rgb = (
        rgb_mean["Red color (0-255)"] / 255.0,
        rgb_mean["Green color (0-255)"] / 255.0,
        rgb_mean["Blue color (0-255)"] / 255.0
    )
    return mean_rgb

def berechne_grauwert(rgb: tuple) -> float:
    """
    Berechnet den Grauwert (Luminanz) aus einem RGB-Tupel (normiert auf [0..1]).
    Formel: 0.299 R + 0.587 G + 0.114 B
    """
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b

def plot_kacheln(klassen, farben, titel, output_png):
    """
    Erstellt eine Kachelgrafik für eine Liste von Farben und speichert sie.

    klassen : Liste der Klassennamen
    farben  : Liste von (r, g, b) beziehungsweise Graustufenwerten
    titel   : Gesamtüberschrift für die Grafik
    output_png : Dateiname der Ausgabedatei
    """
    n = len(klassen)
    fig, axes = plt.subplots(
        nrows=1,
        ncols=n,
        figsize=(n * 2, 3),     # Jede Kachel ca. 2 Zoll breit, Höhe 3 Zoll
        gridspec_kw={'wspace': 0}
    )
    if n == 1:
        axes = [axes]

    for ax, klasse, farbe in zip(axes, klassen, farben):
        # Für Grauwert ist farbe ein Skalar, wir wandeln in RGB-Grauton um
        if isinstance(farbe, tuple):
            rgb = farbe
        else:
            rgb = (farbe, farbe, farbe)
        ax.set_facecolor(rgb)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(
            0.5, -0.15, klasse,
            transform=ax.transAxes,
            ha='center', va='top',
            fontsize=11, fontweight='bold'
        )
    fig.suptitle(titel, fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Grafik gespeichert als '{output_png}'")

if __name__ == "__main__":
    # ------------------------------
    # Einstellungen
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    sep = ";"

    # Ausgabedateien
    output_rgb = "RGB_Kacheln_pro_Klasse.png"
    output_gray = "Grauwert_Kacheln_pro_Klasse.png"

    # Einlesen und Berechnen
    dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
    if not dateien:
        raise FileNotFoundError(f"Keine .txt-Dateien gefunden in '{ordner_pfad}'")

    klassen = []
    mean_rgbs = []
    for dateiname in dateien:
        klasse = get_klasse(dateiname)
        pfad = os.path.join(ordner_pfad, dateiname)
        mean_rgb = lade_mittel_rgb(pfad, sep=sep)
        klassen.append(klasse)
        mean_rgbs.append(mean_rgb)

    # RGB-Kacheln plotten
    plot_kacheln(
        klassen,
        mean_rgbs,
        titel="Durchschnittliche RGB-Farben pro Klasse",
        output_png=output_rgb
    )

    # Grauwert berechnen und plotten
    gray_values = [berechne_grauwert(rgb) for rgb in mean_rgbs]
    plot_kacheln(
        klassen,
        gray_values,
        titel="Durchschnittliche Grauwert-Farben pro Klasse",
        output_png=output_gray
    )