# CodeBTh04

# Github Repo für die Bachelor Thesis Nr 04: Stadtmodel Basel 1960

Dieses Repository dokumentiert die Entwicklung eines Stadtmodells, mit Fokus auf die Automatisierung der einzelnen Prozessschritte mit Python.

Aufgrund der Datenmengen müssen die **Punktwolken** jeweils beim Benutzer **lokal** liegen. Dafür sind die Ordner input und output, jeweils pro Arbeitsschritt vorgesehen. Diese sind im .gitignor auskommentiert und werden auf Github nicht synchornisiert. Entsprechende Resultate sind zeitnah auf dem Server abzulegen.

Die Gliederung des Repo's soll wie folgt nach Hierachie erfolgen:

1. Arbeitspaket: Klassifizierung, Segmentierung, Abstrahierung, Rekonstruktion, GIS-Integration
2. Arbeitsschritt: # logische/nachvollziehbare Gliederung und Namen im Arbeitspaket
3. Arbeitsgrundlage: # klare Struktur mit Input/Output, ev Markdown mit Erläuterungen, .py oder .ipynb-Dateien

## 📁 Projektstruktur Konzept

```text
CodeBTh04/
│
├── README.md                    # Projektübersicht
├── requirements.txt             # Python-Abhängigkeiten
├── build-reqs.sh                # Script zum Erzeugen von requirements.txt
|
├── data/
│   ├── input/              # Lokale Eingangsdaten (nicht versioniert)
│   │   ├── README.md       # Infos zu erwarteten Dateien
│   │   └── .gitkeep        # Platzhalter für leere Ordner
│   └── external/           # Externe Datenquellen (optional)
│       ├── README.md
│       └── .gitkeep
│
├── arbeitspakete/
│   ├── 01_klassifizierung/
│   │   ├── schritt_01_preprocessing/
│   │   │   ├── input/              # Rohdaten/Ausgangsdaten für Arbeitsschritt
│   │   │   ├── output/             # Ergebnisdaten
│   │   │   ├── PyCode/             # Ordner mit verschiedenen PyCodes
│   │   │   ├── analyse.ipynb       # Notebook mit "Clean" Code und Erläuterung
│   │   │   └── erklärung.md        # Beschreibung des Arbeitsschritts
│   │   └── schritt_02_merkmale/
│   │       ├── ...
│   │
│   ├── 02_segmentierung/
│   │   ├── ...
│   │
│   ├── 03_abstrahierung/
│   │   ├── ...
│   │
│   ├── 04_rekonstruktion/
│   │   ├── ...
│   │
│   └── 05_gis_integration/
│       ├── ...
│
├── notebooks/                   # Explorative Analysen außerhalb der AP-Struktur
|    ├── JupyterNB/              # Alle Jupyter-Notebooks
|    ├── PyCode/                 # Alle Python-Skripte
|    └── Other/                  # Sonstige Skripte HTML
|
├── docs/                        # Dokumente, Konzept, ggf. Abbildungen
│   └── konzept.md
└── results/                     # Endergebnisse und Visualisierungen
```

## ⚙️ Setup

1. Repository klonen:

   ```bash
   git clone https://github.com/MarcoStampfli/CodeBTh04.git
   cd CodeBTh04
   ```

2. Virtual Enviorment erstellen:

   ```bash
   conda create --name env_bth04 python=3.9 --yes
   ```

3. Virtual Enviorment activieren:

   ```bash
   conda activate env_bth04
   ```

4. Pakete installieren:

   **Option 1** - Alle Pakete über file beziehen

   ```bash
   pip install -r requirements.txt
   ```

   **Option 2** - Alle Pakete einzeln laden beziehen

   ```bash
   pip install pandas numpy tqdm scikit-learn matplotlib open3d seaborn open3d
   ```

   **Hinweis** - Pakete einzeln Nachträglich instalieren, 3. Env activieren zuerst.

   ```bash
   pip install paketname
   ```
