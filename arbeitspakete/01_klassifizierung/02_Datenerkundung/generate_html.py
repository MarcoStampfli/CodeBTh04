# Liste der Bilddateien
bilder = [
    'Dichteverteilung_Punktnormalen.png', 'Dichteverteilung_RGB.png', 'KDE_Green_vs_Blue.png',
    'KDE_Hue_vs_Saturation.png', 'KDE_Hue_vs_Value.png', 'KDE_Red_vs_Blue.png',
    'KDE_Red_vs_Green.png', 'KDE_Saturation_vs_Value.png', 'KDE_ScanX_vs_hue.png',
    'KDE_ScanY_vs_hue.png', 'KDE_ScanZ_vs_hue.png', 'KDE_Scan_vs_hue.png',
    'KDE_Scan_vs_hue2.png', 'KDE_Znorm_vs_Red.png'
]

# HTML-Grundstruktur
html_code = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Einzelplots Übersicht</title>
</head>
<body>
<h1 style="text-align:center;">Visualisierung: Einzelplots</h1>
"""

# Bilder in 3er-Gruppen anzeigen
for i in range(0, len(bilder), 3):
    gruppe = bilder[i:i+3]
    html_code += '<div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 40px;">\n'

    for bild in gruppe:
        beschriftung = bild.replace(".png", "").replace("_", " ")
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

# HTML-Datei speichern
with open("einzelplot_uebersicht.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("✅ HTML-Datei 'einzelplot_uebersicht.html' wurde erfolgreich erstellt.")
