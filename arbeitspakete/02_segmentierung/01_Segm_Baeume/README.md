# 📄 Segmentierung von Bäumen
Der folgende Python-Code dient der automatisierten Identifikation und Extraktion einzelner Bäume aus der 3D-Punktwolke aus den photogrammetrischen Daten. Er kombiniert rasterbasierte Analyse mit Methoden der Bildverarbeitung, um aus Höheninformationen ein Canopy Height Model (CHM) zu generieren, Baumgipfel zu lokalisieren und Baumkronen mittels Watershed-Segmentierung zu trennen. Das Ergebnis ist eine Liste einzelner Bäume inklusive Höhe, Kronendurchmesser und georeferenzierter Position. Die Visualisierungen werden im Anschluss mit Open3D und matplotlib dargestellt.

## Bäume segmentieren aus Punktwolken

Input: PW mit Vegetation und ohne Boden

````python
# LAS-PW Eingabedatei
PW_Baeume_o_Boden.las
````

## CODE 1:  Segmentieren von Bäumen (zerstreut Verteilt)
Datei: `Code_Einzelbaum.py`

Code 1 funktioniert sehr gut im offenen Gelände, wo Bäume zerstreut und nicht allzu nahe beieinander stehen. Jedoch ist das Einstellen der Parameter wichtig und muss etwas Ausprobiert werden. Vorgängig wurde in Cyclone 3Dr eine Analyse zu den Punktevorkommen der einzeln Bäume gemacht. Auf Grund der Grösse und photogrammetrischer Abdeckung sind dies rund **600-2500 Punkte** pro Baum.
Code ist effizent und ist in rund 10 min durch (PW_Baeume_o_Boden.las,)
**Die Parameter:**

`eps` = Nachbarschaftsradius Werte zwischen 1–3 m, abhängig von Baumabstand und Punktdichte.

`min_samples` = mindest Anzahl Punkte pro Cluster (Baum)

**Schema Ansatz 1**

![Ansatz 1 Bild](../../../docs\img\Segm\Ansatz1_Einzelbaum_Algo.png)


## CODE 2:  Segmentieren von Bäumen (dichter Wald)
Datei: `Code_Wald.py`

Code 2 kombiniert rasterbasierte Analyse mit Methoden der Bildverarbeitung, um aus Höheninformationen ein Canopy Height Model (CHM) zu generieren, Baumgipfel zu lokalisieren und Baumkronen mittels Watershed-Segmentierung zu trennen. Dies ist vorallem da hilfreich wo sich Baumkronen überlappen oder nahe beieinander stehen, das heisst in dichten Waldgebieten.

8-tung: Code ist rechenintensiv und dauert... bei zu kleiner Rasterwahl (0.5= 7min/0.25=2h!)

![Ansatz 2 Bild](../../../docs\img\Segm\Workflow_Watershed.png)


**Die Parameter:**
````Python
res = 0.5              # [m] CHM Rasterauflösung
min_distance = 3.5     # [Pixel] Abstand lokaler Maxima
sigma = 1.0            # Glättung (Gauss-Filter)
min_height = 2.0       # Mindesthöhe für Punkte
eps = 1.5              # DBSCAN: Radius
min_samples = 15       # DBSCAN: Mindestpunkte pro Cluster
diameter_min = 1.5     # [m] minimaler Kronendurchmesser
diameter_max = 10.0    # [m] maximaler Kronendurchmesser
````

**Output**

| Tree_ID | E (Ostwert) | N (Nordwert) | Height_m | Crown_Diameter_m |
|---------|-------------|--------------|----------|------------------|
| 1       | 2613263.90  | 1266088.97   | 290.66   | 2.65             |
| 2       | 2612151.84  | 1266080.35   | 289.57   | 7.65             |

**Schema Ansatz 2**

![Ansatz 2 Bild](../../../docs\img\Segm\Ansatz2_Watershed_Algo.png)



