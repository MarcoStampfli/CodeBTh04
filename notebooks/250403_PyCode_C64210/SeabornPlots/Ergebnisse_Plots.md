# Ergebnisse aus der Analyse zu den Farbräumen

## Dichteverteilung im RGB

Siehe Code: SeabornPlots\00_RGB_Plot.py

<figure align="center">
<img src="Diagramme\Dichteverteilung_RGB.png" alt="KDE: Rot vs Grün" width="500"/>
<figcaption>Abb. 1 - Dichteverteilung der Punktwolke im RGB-Farbraum</figcaption>
</figure>

## Vergleiche im RGB Farbsystem

Siehe Code: SeabornPlots\01_KDE_RGB.py

<figure align="center">
<img src="Diagramme\RvsG_Plot.png" alt="KDE: Rot vs Grün" width="500"/>
<figcaption>Abb. 2 - Verteilung der Punktwolke Rot vs Grün</figcaption>
</figure> => KDE_Red_vs_Green.png
🔴 Die roten Zonen zeigen, wo die meisten Farbwerte liegen → Diese Farben kommen häufiger in deiner Punktwolke vor.

🔹 Die höchsten Dichten scheinen um (50, 75) herum zu liegen, was bedeutet, dass viele Pixel ähnliche Rot-Grün-Kombinationen haben

🔹 Die Daten erstrecken sich diagonal, was bedeutet, dass Rot und Grün oft gemeinsam variieren.

🔹 Falls die Verteilung sich entlang einer Achse häufen würde, wäre eine Farbe dominanter
<figure align="center">
<img src="Diagramme\KDE_Red_vs_Blue.png" alt="KDE: Rot vs Blau" width="500"/>
<figcaption>Abb. 3 - Verteilung der Punktwolke Rot vs Blau</figcaption>
</figure>
<figure align="center">
<img src="Diagramme\KDE_Green_vs_Blue.png" alt="KDE: Grün vs Blau" width="500"/>
<figcaption>Abb. 4 - Verteilung der Punktwolke Grün vs Blau</figcaption>
</figure>

## Vergleiche im HSV Farbsystem

Siehe Code: **SeabornPlots\02_KDE_HSV.py**

Welche Farben sind dominant und wie gesättigt sind sie?

<figure align="center">
<img src="Diagramme\KDE_Hue_vs_Saturation.png" alt="KDE: Rot vs Grün" width="500"/>
<figcaption>Abb. 5 - Verteilung der Punktwolke Hue vs Saturation</figcaption>
</figure>

Wie verteilen sich die Farben über verschiedene Helligkeiten?

<figure align="center">
<img src="Diagramme\KDE_Hue_vs_Value.png" alt="KDE: Rot vs Grün" width="500"/>
<figcaption>Abb. 6 - Verteilung der Punktwolke Hue vs Value</figcaption>
</figure>

Gibt es mehr helle oder dunkle, stark oder schwach gesättigte Farben?

<figure align="center">
<img src="Diagramme\KDE_Saturation_vs_Value.png" alt="KDE: Rot vs Grün" width="500"/>
<figcaption>Abb. 7 - Verteilung der Punktwolke Saturation vs Value</figcaption>
</figure>
