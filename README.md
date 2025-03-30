# CodeBTh04
# Github Repo für die Bachelor Thesis Nr 04: Stadtmodel Basel 1960
Dieses Repository dokumentiert die Entwicklung eines Stadtmodells, mit Fokus auf die Automatisierung der einzelnen Prozessschritte mit Python.

Die Gliederung des Repo's soll wie folgt nach Hierachie erfolgen:
1. Arbeitspaket: Klassifizierung, Segmentierung, Abstrahierung, Rekonstruktion, Gis Integration
2. Arbeitsschritt: # logische/nachvollziehbare Gliederung und Namen im Arbeitspaket
3. Arbeitsgrundlage: # klare Struktur mit Input/Output, ev Markdown mit Erläuterungen, .py oder .ipynb-Dateien
  
## 📁 Projektstruktur

```text
stadtmodell/
│
├── README.md                    # Projektübersicht
├── requirements.txt             # Python-Abhängigkeiten
├── build-reqs.sh                # Script zum Erzeugen von requirements.txt
│
├── arbeitspakete/
│   ├── 01_klassifizierung/
│   │   ├── schritt_01_preprocessing/
│   │   │   ├── input/              # Rohdaten
│   │   │   ├── output/             # Ergebnisdaten
│   │   │   ├── analyse.ipynb       # Notebook zur Analyse
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
├── docs/                        # Dokumente, Konzept, ggf. Abbildungen
│   └── konzept.md
├── data/                        # Zentrale Datenbasis (optional verlinkt)
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
