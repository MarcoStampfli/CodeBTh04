# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================
"""
Abstract:
Dieses Skript dient der automatisierten Extraktion und tabellarischen Zusammenstellung von Auswertungsparametern und 
Ergebnisdaten aus einer hierarchischen Ordnerstruktur, wie sie typischerweise in Workflows der Einzelbaumsegmentierung vorkommt. 
Es durchsucht die Output-Verzeichnisse nach Dateien, die spezifische Parameter im Dateinamen kodieren, extrahiert diese Parameter 
per regulärem Ausdruck und ergänzt sie mit weiteren Informationen wie der Anzahl der detektierten Bäume (aus zugehörigen CSV-Dateien) 
sowie mit Pfaden zu Ergebnisbildern. Die gesammelten Daten werden zu einer übersichtlichen Tabelle zusammengefasst und als CSV-Datei gespeichert. 
Das Ergebnis ist eine zentrale Parameter- und Ergebnistabelle, die den Vergleich verschiedener Segmentierungsläufe 
sowie die weiterführende Analyse und Dokumentation effizient unterstützt.
"""

import os
import re
import pandas as pd

def parse_filename(filename):
    pattern = (r"Parameter_res(?P<res>[0-9.]+)_minPix(?P<min_distance>[0-9]+)_sig(?P<sigma>[0-9.]+)"
               r"_minH(?P<min_height>[0-9.]+)_eps(?P<eps>[0-9.]+)_minSam(?P<min_samples>[0-9]+)"
               r"_DM(?P<diameter_min>[0-9.]+)bis(?P<diameter_max>[0-9.]+)")
    match = re.search(pattern, filename)
    if match:
        return match.groupdict()
    else:
        return None

def count_csv_rows(csv_path):
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            count = sum(1 for _ in f) - 1
            return int(count) if count >= 0 else 0
    except Exception:
        return 0

def extract_params_from_output(output_dir):
    data = []
    for ordner in os.listdir(output_dir):
        ordner_path = os.path.join(output_dir, ordner)
        if not os.path.isdir(ordner_path):
            continue

        # Suche nach einer Parameterdatei
        for file in os.listdir(ordner_path):
            if "Parameter_res" in file:
                params = parse_filename(file)
                if params:
                    params['Ordnername'] = ordner

                    # Finde zugehörige CSV-Datei (z.B. baumdaten_watershed_RunID_{ordner}.csv)
                    csv_file = None
                    for f in os.listdir(ordner_path):
                        if f.endswith('.csv') and f"RunID_{ordner}" in f:
                            csv_file = os.path.join(ordner_path, f)
                            break
                    # HIER: KEIN None, sondern immer int!
                    params['Trees'] = int(count_csv_rows(csv_file)) if csv_file else 0

                    # Füge Bildpfad hinzu
                    img_path = os.path.join(ordner_path, 'step0_PW_vs_Kataster.png')
                    params['PW vs Trees'] = img_path if os.path.isfile(img_path) else None

                    params['Dateiname'] = file
                    data.append(params)
    columns = [
        "Ordnername", "Trees", "res", "min_distance", "sigma", "min_height", "eps",
        "min_samples", "diameter_min", "diameter_max", "PW vs Trees", "Dateiname"
    ]
    df = pd.DataFrame(data)
    # Nochmals sicherstellen:
    df['Trees'] = df['Trees'].fillna(0).astype(int)
    df = df[columns]
    return df

# Aufruf Funktion:
output_dir = r"C:\Users\marco\Documents\CodeBTh04\arbeitspakete\02_segmentierung\01_Segm_Baeume\output"
df = extract_params_from_output(output_dir)
df.to_csv(r"arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Resultate\parameter_tabelle.csv", index=False)
print(df)
