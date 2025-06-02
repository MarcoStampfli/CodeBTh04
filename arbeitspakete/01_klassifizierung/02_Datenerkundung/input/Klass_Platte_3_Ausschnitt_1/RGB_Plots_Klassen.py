#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skript: durchschnittliche RGB-Farben pro Klasse visualisieren

Dieses Skript liest alle .txt-Dateien in einem angegebenen Ordner ein (die Dateien enthalten
HSV- und RGB-Daten pro Pixel), berechnet für jede Klasse den Durchschnitt der RGB-Farben
und erzeugt daraus ein Balkendiagramm, in dem jeder Balken die durchschnittliche
RGB-Farbe der jeweiligen Klasse darstellt.

Voraussetzungen:
- Die Textdateien befinden sich in `ordner_pfad` und sind semikolon-separiert.
- Jede Datei liefert beim Einlesen mit Pandas 12 Spalten in dieser Reihenfolge:
  X, Y, Z, R, G, B, Xscan, Yscan, Zscan, Hue, Saturation, Value
- Die Klassenbezeichnung wird aus dem Dateinamen gewonnen, indem "_HSV.txt" abgeschnitten
  und der letzte Unterstrich-Teil verwendet wird (z.B. "XYZ_Bäume_HSV.txt" → "Bäume").

Einsatz:
    python plot_avg_rgb_per_class.py

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
    Annahme: Dateiname endet auf "_HSV.txt", der Klassenname steht nach dem letzten Unterstrich.
    Beispiel: "Klass_Platte_3_Ausschnitt_1_Bäume_HSV.txt" → "Bäume"
    """
    basis = dateiname.replace("_HSV.txt", "")
    return basis.split("_")[-1]

def lade_mittel_rgb_und_hue(dateipfad: str, sep: str = ";"):
    """
    Liest die HSV-Datei ein und gibt zurück:
      - mean_rgb: Tuple (r, g, b) mit den normierten Mittelwerten [0..1]
      - hues_rad: NumPy-Array mit allen Hue-Werten in Radiant (falls benötigt)
    Erwartet 12 Spalten beim Einlesen:
      [X, Y, Z, R, G, B, Xscan, Yscan, Zscan, Hue, S, V]
    """
    df = pd.read_csv(dateipfad, sep=sep, decimal=".", header=None)
    if df.shape[1] != 12:
        raise ValueError(
            f"Datei '{os.path.basename(dateipfad)}' enthält nach Einlesen nur {df.shape[1]} Spalten statt 12."
        )
    # Spalten beschriften, um Zugriff zu erleichtern
    df.columns = [
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
        "X scan dir", "Y scan dir", "Z scan dir",
        "Hue (°)", "Saturation (%)", "Value (%)"
    ]
    # RGB-Mittelwerte berechnen und auf [0,1] normieren
    rgb_mean = df[["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)"]].mean()
    mean_rgb = (
        rgb_mean["Red color (0-255)"] / 255.0,
        rgb_mean["Green color (0-255)"] / 255.0,
        rgb_mean["Blue color (0-255)"] / 255.0
    )
    # Hue in Radiant (optional, falls man Hue-Verteilungen braucht)
    hues_rad = np.deg2rad(df["Hue (°)"].values)
    return mean_rgb, hues_rad

def main():
    # ------------------------------
    # 1) Einstellungen: Pfade und Parameter
    # Ordner, in dem die HSV-Textdateien liegen
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    # Separator beim Einlesen; bei semikolon-getrennten Dateien:
    sep = ";"

    # Ziel-Datei zum Speichern des Plots
    output_png = "Durchschnittliche_RGB_Farben_pro_Klasse.png"

    # ------------------------------
    # 2) Dateinamen einlesen und Klassen extrahieren
    dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
    if len(dateien) == 0:
        raise FileNotFoundError(f"Keine .txt-Dateien gefunden in '{ordner_pfad}'")

    klassen = []
    mean_rgbs = []
    # optional: hues_rad_dict, falls man Hue-Verteilungen später braucht
    hues_rad_dict = {}

    for dateiname in dateien:
        klasse = get_klasse(dateiname)
        dateipfad = os.path.join(ordner_pfad, dateiname)
        mean_rgb, hues_rad = lade_mittel_rgb_und_hue(dateipfad, sep=sep)
        klassen.append(klasse)
        mean_rgbs.append(mean_rgb)
        hues_rad_dict[klasse] = hues_rad

    # In konstanter Reihenfolge plotten (z.B. nach Eingangsreihenfolge der Dateien).
    # Eventuell: klassen, mean_rgbs gemeinsam sortieren, falls gewünscht.

    # ------------------------------
    # 3) Plot: horizontale Balken mit RGB-Farben
    fig, ax = plt.subplots(figsize=(10, 2.5))
    # y-Positionen von unten nach oben (0,1,2,...), invertiert, damit erstes Element oben steht
    y_pos = np.arange(len(klassen))

    # Breite jedes Balkens entspricht 1 (wir brauchen nur Farbrechtecke)
    widths = np.ones_like(y_pos)

    # Zeichne horizontalen Balken für jede Klasse, farbig nach mean_rgb
    ax.barh(
        y=y_pos,
        width=widths,
        height=0.8,
        left=0,
        color=mean_rgbs,
        edgecolor="none"
    )

    # Achsen anpassen:
    # - x-Achse entfernen, da sie irrelevant ist (alle Breiten sind 1)
    # - y-Achse die Klassenbezeichnungen anzeigen
    ax.set_xticks([])
    ax.set_xlim(0, 1)

    # y-Ticks mittig in den Balken platzieren
    ax.set_yticks(y_pos)
    ax.set_yticklabels(klassen, fontsize=10)

    # Die Reihenfolge so drehen, dass die erste Klasse oben steht
    ax.invert_yaxis()

    # Rahmen auf allen Seiten ausblenden
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Titel des Plots
    ax.set_title("Durchschnittliche RGB-Farben pro Klasse", fontsize=14, pad=10)

    plt.tight_layout()
    # Speichere die Abbildung als PNG
    fig.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"Plot gespeichert als '{output_png}'")

    # Optional: zeige Plot interaktiv (falls gewünscht)
    # plt.show()

if __name__ == "__main__":
    main()
