import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
# Ordner mit deinen .txt-Dateien (Raw-String)
ordner_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\input\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"
output_pfad = r"arbeitspakete\01_klassifizierung\02_Datenerkundung\output"

dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]
if len(dateien) == 0:
    raise FileNotFoundError(f"Keine .txt-Dateien gefunden in {ordner_pfad}")

def get_klasse(dateiname):
    return dateiname.replace("_HSV.txt", "").split("_")[-1]

# Unterteilung: „Schrägdach“ und „Wasser“, Rest
subset1_names = ["Schrägdach", "Wasser"]
dateien_subset1 = [f for f in dateien if get_klasse(f) in subset1_names]
dateien_subset2 = [f for f in dateien if get_klasse(f) not in subset1_names]

def load_data(dateipfad, sep=";"):
    """
    Liest eine HSV-Datei ein und gibt zurück:
      - hues_rad: NumPy-Array der Hue-Werte in Radiant
      - mean_rgb: Tuple mit den normalisierten Mittelwerten (r, g, b), jeweils [0..1]
    """
    df = pd.read_csv(dateipfad, sep=sep, decimal=".", header=None)
    if df.shape[1] != 12:
        raise ValueError(
            f"Datei '{os.path.basename(dateipfad)}' hat nach Einlesen nur {df.shape[1]} Spalten statt 12."
        )
    df.columns = [
        "X coordinate", "Y coordinate", "Z coordinate",
        "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
        "X scan dir", "Y scan dir", "Z scan dir",
        "Hue (°)", "Saturation (%)", "Value (%)"
    ]
    # Hue in Radiant
    hues_rad = np.deg2rad(df["Hue (°)"].values)
    # Mittelwerte der RGB-Spalten und auf [0,1] normieren
    rgb_mean = df[["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)"]].mean()
    mean_rgb = (rgb_mean["Red color (0-255)"] / 255.0,
                rgb_mean["Green color (0-255)"] / 255.0,
                rgb_mean["Blue color (0-255)"] / 255.0)
    return hues_rad, mean_rgb

# Lade alle Hue-Werte und Mittel-RGB in Dictionaries
hues_rad_dict = {}
mean_rgb_dict = {}
for dateiname in dateien:
    dateipfad = os.path.join(ordner_pfad, dateiname)
    hues_rad, mean_rgb = load_data(dateipfad, sep=";")
    hues_rad_dict[dateiname] = hues_rad
    mean_rgb_dict[dateiname] = mean_rgb

# Gemeinsame Bin-Grenzen (36 Sektoren à 10°)
n_bins = 36
bins_rad = np.linspace(0, 2 * np.pi, n_bins + 1)
width = bins_rad[1] - bins_rad[0]  # Breite eines Sektors

# ------------------------------
# 1) Figur 1: Schrägdach & Wasser (2 Spalten, 1 Zeile), radial limit = 3
threshold1 = 0.5  # nur Balken ≥ 0.5 anzeigen

fig1, axes1 = plt.subplots(
    nrows=1,
    ncols=2,
    subplot_kw={'projection': 'polar'},
    figsize=(8, 4)
)
fig1.suptitle("Untersuchung der Farbwerte (Hue °)", fontsize=14, y=0.98)

for ax, dateiname in zip(axes1, dateien_subset1):
    hues_rad = hues_rad_dict[dateiname]
    mean_rgb = mean_rgb_dict[dateiname]
    # Manuelles Histogramm (Dichte) berechnen
    counts, _ = np.histogram(hues_rad, bins=bins_rad, density=True)
    angles = (bins_rad[:-1] + bins_rad[1:]) / 2  # Mittelpunkte der Sektoren
    
    # Nur die Balken zeichnen, deren Dichte ≥ threshold1 ist
    mask = counts >= threshold1
    ax.bar(
        angles[mask],
        counts[mask],
        width=width,
        bottom=0,
        color=mean_rgb,       # Balken einfärben nach Mittel-RGB
        alpha=0.7
        # edgecolor='black'
    )
    
    # 1.1) Radial-Limit und reduzierte y-Ticks
    ax.set_ylim(0, 3.75)
    ax.set_yticks([1.0, 2.0, 3.0])
    ax.set_yticklabels(["1", "2", "3"])
    
    # 1.2) Gridlinien hinter die Balken legen
    ax.set_axisbelow(True)
    ax.grid(True, color="gray", linestyle="--", linewidth=0.5)
    
    # 1.3) 0° oben, Winkel im Uhrzeigersinn
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    
    # 1.4) Winkel-Ticks alle 30°
    winkel_grad = np.arange(0, 360, 30)
    ax.set_xticks(np.deg2rad(winkel_grad))
    # Tick-Labels: Rot (0°), Grün (120°), Blau (240°), sonst Gradzahl
    labels = []
    for w in winkel_grad:
        if w == 0:
            labels.append("Rot")
        elif w == 120:
            labels.append("Grün")
        elif w == 240:
            labels.append("Blau")
        else:
            labels.append(f"{w}°")
    ax.set_xticklabels(labels)
    
    # 1.5) Titel pro Subplot (fett)
    klasse = get_klasse(dateiname)
    ax.set_title(klasse, va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
# 1.6) Grafik abspeichern (im aktuellen Arbeitsverzeichnis)
plot_path1 = os.path.join(output_pfad, "HUE_diagramm_Schraegdach_Wasser_RGB_Balken.png")
fig1.savefig(plot_path1, dpi=300, bbox_inches='tight')
plt.show()

# ------------------------------
# 2) Figur 2: Restliche Klassen (3 Spalten × 2 Zeilen), radial limit = 1.5
threshold2 = 0.25  # nur Balken ≥ 0.25 anzeigen

n_rest = len(dateien_subset2)
fig2, axes2 = plt.subplots(
    nrows=2,
    ncols=3,
    subplot_kw={'projection': 'polar'},
    figsize=(12, 8)
)
axes2 = axes2.flatten()
fig2.suptitle("Untersuchung der Farbwerte (Hue °)", fontsize=14, y=0.98)

for idx, dateiname in enumerate(dateien_subset2):
    ax = axes2[idx]
    hues_rad = hues_rad_dict[dateiname]
    mean_rgb = mean_rgb_dict[dateiname]
    counts, _ = np.histogram(hues_rad, bins=bins_rad, density=True)
    angles = (bins_rad[:-1] + bins_rad[1:]) / 2
    
    mask = counts >= threshold2
    ax.bar(
        angles[mask],
        counts[mask],
        width=width,
        bottom=0,
        color=mean_rgb,       # Balken einfärben nach Mittel-RGB
        alpha=0.7
        # edgecolor='black'
    )
    
    # 2.1) Radial-Limit und reduzierte y-Ticks
    ax.set_ylim(0, 1.5)
    ax.set_yticks([0.5, 1.0, 1.5])
    ax.set_yticklabels(["0.5", "1.0", ""])
    
    # 2.2) Gridlinien hinter die Balken legen
    ax.set_axisbelow(True)
    ax.grid(True, color="gray", linestyle="--", linewidth=0.5)
    
    # 2.3) 0° oben, Winkel im Uhrzeigersinn
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    
    # 2.4) Winkel-Ticks
    winkel_grad = np.arange(0, 360, 30)
    ax.set_xticks(np.deg2rad(winkel_grad))
    labels = []
    for w in winkel_grad:
        if w == 0:
            labels.append("Rot")
        elif w == 120:
            labels.append("Grün")
        elif w == 240:
            labels.append("Blau")
        else:
            labels.append(f"{w}°")
    ax.set_xticklabels(labels)
    
    # 2.5) Titel pro Subplot (fett)
    klasse = get_klasse(dateiname)
    ax.set_title(klasse, va='bottom', fontsize=10, fontweight='bold')

# 2.6) Leere Subplots ausblenden
for idx_extra in range(n_rest, len(axes2)):
    axes2[idx_extra].axis('off')

# 2.7) Vertikalen Abstand (hspace) erhöhen
plt.tight_layout()
plt.subplots_adjust(top=0.85, hspace=0.4)

plot_path2 = os.path.join(output_pfad, "HUE_diagramm_restl_Klassen_RGB_Balken.png")
fig2.savefig(plot_path2, dpi=300, bbox_inches='tight')
plt.show()
