# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
"""
Skript: Durchschnittliche RGB-Farben pro Klasse als farbige Kacheln darstellen

Dieses Skript liest alle .txt-Dateien in einem angegebenen Ordner ein (jede Datei enthält
pro Pixel XY Z-Koordinaten, RGB- und HSV-Werte). Für jede Klasse wird der Durchschnitt der
RGB-Farben berechnet und dann in einer Grafik als gleich große farbige Kachel dargestellt.
Unter jeder Kachel steht der Klassenname als Untertitel.

Voraussetzungen:
- Die Textdateien liegen im Ordner `ordner_pfad` und sind semikolon-getrennt.
- Beim Einlesen mit Pandas entstehen genau 12 Spalten in der Reihenfolge
  [X, Y, Z, R, G, B, Xscan, Yscan, Zscan, Hue, Saturation, Value].
- Der Klassenname wird aus dem Dateinamen gewonnen, indem "_HSV.txt" abgeschnitten
  und der letzte Unterstrich-Teil verwendet wird (z. B. "…_Bäume_HSV.txt" → "Bäume").

Einsatz:
    python plot_rgb_tiles_per_class.py

Autor: ChatGPT (angepasst auf Nutzerwunsch)
Datum: 2025-06-02
"""

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

def main():
    # ------------------------------
    # 1) Einstellungen: Pfade und Parameter
    # Pfad zu deinem Ordner mit den HSV-Textdateien
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    sep = ";"  # Separator zum Einlesen der TXT-Dateien

    # Name der Ausgabedatei (PNG)
    output_png = "RGB_Kacheln_pro_Klasse.png"

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
    # 3) Plot-Vorbereitung: Anzahl der Klassen ermitteln
    n = len(klassen)
    # Bestimme das Gitternetz: eine Reihe mit n Spalten
    fig, axes = plt.subplots(
        nrows=1,
        ncols=n,
        figsize=(n * 2, 3),     # Jede Kachel ca. 2 Zoll breit, Höhe insgesamt 3 Zoll
        gridspec_kw={'wspace': 0}  # horizontaler Abstand zwischen den Kacheln
    )

    # Falls nur eine Klasse, stellen wir axes zu einer Liste um
    if n == 1:
        axes = [axes]

    # ------------------------------
    # 4) Für jede Klasse eine Kachel einfärben und Namen darunter schreiben
    for ax, klasse, rgb in zip(axes, klassen, mean_rgbs):
        # 4.1) Volle Fläche einfärben
        ax.set_facecolor(rgb)

        # 4.2) Achsen unsichtbar schalten (kein Ticks, keine Linien)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # 4.3) Klassenname als Untertitel (zentriert unten)
        #      Wir platzieren den Text etwas außerhalb des Achsenbereichs (transform=ax.transAxes)
        ax.text(
            0.5, -0.15, klasse,
            transform=ax.transAxes,
            ha='center', va='top',
            fontsize=11, fontweight='bold'
        )

    # ------------------------------
    # 5) Gesamt-Titel und Speicherung
    fig.suptitle("Durchschnittliche RGB-Farben pro Klasse", fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"Die Grafik wurde gespeichert als '{output_png}'")
    # plt.show()  # Optional: interaktive Anzeige

if __name__ == "__main__":
    main()
