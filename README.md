# CodeBTh04
# Github Repo für die Bachelor Thesis Nr 04: Stadtmodel Basel 1960
Dieses Repository dokumentiert die Entwicklung eines Stadtmodells, mit Fokus auf die Automatisierung der einzelnen Prozessschritte.

## 🗂 Projektstruktur
**provisorisch**
- `src/`: Enthält alle relevanten Skripte zur Datenverarbeitung, Analyse und Visualisierung.
- `notebooks/`: Explorative Analysen und Prototypen.
- `data/`: Eingabedaten (Hinweis: größere Dateien evtl. über externen Link zugänglich).
- `results/`: Modelloutputs, Karten und Abbildungen.
- `docs/`: Ergänzende Dokumentation und Konzepte.

CodeBTh04/
│
├── README.md
├── .gitignore
├── docs/                 # Zusatzdokumentation, evtl. PDF/MD
│   └── konzept.md
├──Klassifizierung
  ├── data/                 # Input-Daten, z. B. GeoJSON, CSV etc. (oder verlinkt)
  ├── src/                  # Quellcode
  │   ├── preprocessing/    # Datenbereinigung, -transformation
  │   ├── analysis/         # Auswerteskripte, Modelle etc.
  │   └── visualization/    # Karten, Diagramme etc.
  ├── notebooks/            # Jupyter Notebooks für Exploration / Prototypen
  └── results/              # Outputs: Karten, Charts, Modelloutputs etc.


## ⚙️ Setup

1. Repository klonen:
   ```bash
   git clone https://github.com/MarcoStampfli/CodeBTh04.git
   cd CodeBTh04
   ```

2. Virtual Enviorment erstellen:
   ```bash
   conda create --name env_bth04 python=3.9 -y
   ```

3. Virtual Enviorment activieren:
   ```bash
   conda activate env_bth04
   ```

4. Packages installieren:
   ```bash
   pip install pandas numpy tqdm scikit-learn matplotlib open3d seaborn
   ```
