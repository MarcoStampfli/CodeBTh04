# 📄 Punktwolkendaten mittels KMeans-Clustering Klassifizieren

Dieses Skript dient der automatisierten Farbklassifizierung von 3D-Punktwolken, indem es ein KMeans-Clustering auf der Hue-Komponente des HSV-Farbraums durchführt. Die zugrunde liegende Punktwolke enthält bereits normalisierte Farbwerte sowie zuvor berechnete Hue-, Saturation- und Value-Werte (HSV). Die Klassifizierung erfolgt anhand des Farbtons Hue oder unter Angabe von anderen Variablen. Mit einer einstellbaren Anzahl von Clustern (z. B. 3–10) wir definiert wieviele Klassen gesplittet werden sollen.

Nach dem Clustering werden:

- Die resultierenden Cluster-IDs der Punktwolke zugewiesen

- Einzelne Textdateien pro Cluster erstellt und gespeichert

- Optional kann eine Wertebereichs-Statistik (RGB- und HSV-Min/Max je Cluster) erzeugt werden

- Das Skript bietet darüber hinaus eine Option zur Visualisierung mittels Open3D, bei der die Cluster farblich codiert angezeigt werden.
