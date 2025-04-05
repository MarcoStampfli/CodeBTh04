# 🔍 Erklärung – Schritt 01 Datenaufbereitung

Was passiert in diesem Schritt?

Wir bereiten die Daten so auf, das wir die Punktwolke als Grundlage im .txt Format haben. Die Punktwolke wurde aus Leica 3Dr im txt-Format exportiert und hat das folgende Format:

<figure align="center">
<img src="docs\img\Export_PW_3Dr_Screenshot 2025-03-17 133131.png" alt="Export aus Leica 3Dr" width="500"/>
<figcaption>Abb. 1 - Export aus Leica 3Dr</figcaption>
</figure>

Basis-Exportdateien sollen nach folgenden Schema gespeichert werden und jeweils Sinnvolle kurzformen verwenden:

**PW = Punktwolke**

**P3A1 = Platte 3, Ausschnitt 1**

```text
# Datenart_Kachel.txt

PW_P3A1.txt
```

Die txt-Datei sollte so aus sehen:

| KOO     | RBG 0-255 | Normalen 0-1 |
| ------- | --------- | ------------ |
| X, Y, Z | R, G, B   | x, y, z      |
| ...     | ...       | ...          |

Als Nächstes Normalisieren wir die Werte und fügen eine neue Spalte mit HSV-Werten hinzu und speichern sie.

```text
# Datei speichern als:

PW_P3A1_normalisiert.txt
```

Die txt-Datei sollte nun so aus sehen:

| KOO     | RBG 0-1 | HSV 0-1 | Normalen 0-1 |
| ------- | ------- | ------- | ------------ |
| X, Y, Z | R, G, B | H, S, V | x, y, z      |
| ...     | ...     | ...     | ...          |
