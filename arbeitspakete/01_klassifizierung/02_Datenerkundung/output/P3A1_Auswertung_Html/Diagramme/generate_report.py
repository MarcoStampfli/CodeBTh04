from collections import defaultdict

# Liste der Dateinamen
dateien = [
    'P3A1_Klasse_Bäume_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Bäume_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Bäume_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Fassade_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Fassade_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Fassade_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Flachdach_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Flachdach_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Flachdach_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Ground_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Ground_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Ground_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Schrägdach_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Schrägdach_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Schrägdach_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Strasse_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Strasse_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Strasse_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Trottoir_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Trottoir_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Trottoir_KDE_ScanXYZ_vs_hue.png',
    'P3A1_Klasse_Wasser_Dichteverteilung_RGB.png',
    'P3A1_Klasse_Wasser_Dichteverteilung_XYZ_Norm.png',
    'P3A1_Klasse_Wasser_KDE_ScanXYZ_vs_hue.png'
]

# Gruppieren nach Klassenname (z. B. "Bäume")
klassen_dict = defaultdict(list)

for datei in dateien:
    teile = datei.split("_")
    klasse = teile[2]  # z. B. "Bäume"
    klassen_dict[klasse].append(datei)

# HTML generieren
html_code = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Plot-Übersicht</title>
</head>
<body>
"""

for klasse, bilder in klassen_dict.items():
    html_code += f"<h2>Plots der Klasse: {klasse}</h2>\n"
    html_code += '<div style="display: flex; gap: 20px; margin-bottom: 40px;">\n'

    for bild in sorted(bilder):  # sortiert für gleichbleibende Reihenfolge
        beschriftung = bild.split("_")[-1].replace(".png", "").replace("KDE", "KDE-Plot")
        html_code += f"""
        <figure style="text-align: center;">
            <img src="Diagramme/{bild}" width="300">
            <figcaption>{beschriftung}</figcaption>
        </figure>
        """

    html_code += "</div>\n"

html_code += """
</body>
</html>
"""

# HTML speichern
with open("diagramm_uebersicht.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("✅ HTML-Datei 'diagramm_uebersicht.html' wurde erfolgreich erstellt.")
