# 🔍 Erklärung – Schritt 01

Was passiert in diesem Schritt?

flowchart TD
A([Starte Skript])
B([Baumdaten aus CSV laden])
C([Gelände-Mesh (OBJ) laden])
D([Raycasting-Szene erzeugen])
E([Strahlen nach unten definieren])
F([Raycasting: Baumhöhe berechnen])
G([Modellparameter berechnen\n(z.B. Z neu, Höhen, Durchmesser, Farbe)])
H([Neue CSV speichern])
I([Fertig])

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
