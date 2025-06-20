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
    """
    Konvertiert sRGB-Wert (0–1) in linearen RGB-Wert gemäß Rec.709.
    """
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def berechne_grauwert_wissenschaftlich(rgb: tuple) -> tuple:
    """
    Berechnet Grauwert aus linearem RGB gemäß Rec.709 (physikalisch korrekt).
    Rückgabe: (grau, grau, grau) im Bereich 0–1
    """
    r_lin = srgb_to_linear(rgb[0])
    g_lin = srgb_to_linear(rgb[1])
    b_lin = srgb_to_linear(rgb[2])
    gray = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    return (gray, gray, gray)

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
    # 🔧 Einstellungen
    bool = False # True = wissenschaftliche Graustufenberechnung
    wissenschaftlich = bool 
    ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
    sep = ";"
    output_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\output"
    # Stelle sicher, dass der Ordner existiert:
    os.makedirs(output_pfad, exist_ok=True)
    # dateiname = "RGB_und_Grauwert_Kacheln_pro_Klasse_wissenschaftlich.png"
    dateiname = "Doku_RGB_und_Grauwert_Kacheln_pro_Klasse.png"
    datei_pfad = os.path.join(output_pfad, dateiname)


    # ------------------------------
    # 📥 Daten einlesen
    dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
    if len(dateien) == 0:
        raise FileNotFoundError(f"Keine .txt-Dateien gefunden in '{ordner_pfad}'")

    klassen = []
    mean_rgbs = []
    mean_grays = []

    for dateiname in dateien:
        klasse = get_klasse(dateiname)
        dateipfad = os.path.join(ordner_pfad, dateiname)
        mean_rgb = lade_mittel_rgb(dateipfad, sep=sep)

        # Grauwertberechnung nach Wahl
        if wissenschaftlich:
            gray_rgb = berechne_grauwert_wissenschaftlich(mean_rgb)
        else:
            gray = 0.299 * mean_rgb[0] + 0.587 * mean_rgb[1] + 0.114 * mean_rgb[2]
            gray_rgb = (gray, gray, gray)

        klassen.append(klasse)
        mean_rgbs.append(mean_rgb)
        mean_grays.append(gray_rgb)

    # ------------------------------
    # 📊 Plot erstellen (3 Zeilen: Farbe – Beschriftung – Graustufe)
    n = len(klassen)
    fig, axes = plt.subplots(nrows=2, ncols=n, figsize=(n * 2, 4),
                         gridspec_kw={'hspace': 0.1, 'wspace': 0})

    # Falls nur 1 Spalte
    if n == 1:
        axes = np.array([[axes[0]], [axes[1]]])

    # Obere Zeile = RGB + Titel
    for ax, rgb, klasse in zip(axes[0], mean_rgbs, klassen):
        ax.set_facecolor(rgb)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(klasse, fontsize=11, fontweight='bold')

    # Untere Zeile = Graustufen
    for ax, gray in zip(axes[1], mean_grays):
        ax.set_facecolor(gray)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    # ------------------------------
    # 💾 Speichern
    fig.suptitle("Durchschnittliche RGB-Farben & Grauwerte pro Klasse", fontsize=14, y=1.05)
    plt.tight_layout()
    fig.savefig(datei_pfad, dpi=300, bbox_inches='tight')
    print(f"✅ Grafik gespeichert als '{dateipfad}'")

if __name__ == "__main__":
    main()
