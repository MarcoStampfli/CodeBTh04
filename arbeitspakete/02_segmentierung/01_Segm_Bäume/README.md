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


## CODE 2:  Segmentieren von Bäumen (dichter Wald)
Datei: `Code_Wald.py`

Code 2 kombiniert rasterbasierte Analyse mit Methoden der Bildverarbeitung, um aus Höheninformationen ein Canopy Height Model (CHM) zu generieren, Baumgipfel zu lokalisieren und Baumkronen mittels Watershed-Segmentierung zu trennen. Dies ist vorallem da hilfreich wo sich Baumkronen überlappen oder nahe beieinander stehen, das heisst in dichten Waldgebieten.

8-tung: Code ist rechenintensiv und dauert...

**Die Parameter:**

`res` = Rasterauflösung des CHM's

`min_distance` = mindest Abstand der Peaks (Baumspitzen)

`sigma` = Glätungsindex für Gauss-Filter

````Python
Output-Ordner: output
Lade Punktwolke ...
Anzahl Punkte nach Filter (>2 m): 7525918
Erzeuge Canopy Height Model (CHM) ...
CHM erstellt (5610 x 4036 Zellen, Auflösung 0.25 m)
Suche lokale Maxima ...
Gefundene Baumgipfel: 31931
Starte Watershed-Segmentierung ...
Segmentierte Baumregionen: 31931
Extrahiere Baumdaten ...
Analysiere Bäume: 100%|███████████████████████████████████████████████████████████████████████████| 31932/31932 [2:07:22<00:00,  4.18it/s]   
Baumdaten gespeichert in: output\baumdaten_watershed.csv (21447 Bäume)
Gesamtlaufzeit: 127 Minuten und 32.83 Sekunden  
Erzeuge 2D-Visualisierung (CHM + Baumgipfel) ...
Visualisierung gespeichert in: output\chm_baumgipfel.png
Starte Open3D-Visualisierung ...
````