"""
Abstract:
Dieses Skript generiert automatisiert einen HTML-Report aus einer hierarchisch aufgebauten Ergebnisstruktur von Segmentierungsläufen. 
Für jeden Auswertungsordner werden relevante Parameter direkt aus den Dateinamen extrahiert, die Anzahl der detektierten Bäume aus 
zugehörigen CSV-Dateien bestimmt und die wichtigsten Ergebnisbilder (z. B. Segmentierungs- und Qualitätskontrollplots) übersichtlich 
und nebeneinander angezeigt. Die Auswertung erfolgt dabei dynamisch und ist unabhängig von der Anzahl oder Benennung der Ordner. 
Das Resultat ist ein übersichtlicher, browserbasierter Gesamtbericht, der sich besonders zur schnellen visuellen und tabellarischen 
Bewertung sowie zum Vergleich unterschiedlicher Parameterläufe eignet.
"""

import os
import re
import pandas as pd
from pathlib import Path


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

def html_for_folder(ordner_path, ordnername, ziel_html):
    param_file = next((f for f in os.listdir(ordner_path) if "Parameter_res" in f), None)
    params = parse_filename(param_file) if param_file else {}
    csv_file = next((f for f in os.listdir(ordner_path) if f.endswith('.csv') and f"RunID_{ordnername}" in f), None)
    trees = count_csv_rows(os.path.join(ordner_path, csv_file)) if csv_file else 0

    html = f"<h2>{ordnername} – extrahierte Bäume: {trees}</h2>\n"
    if params:
        param_text = ", ".join([f"{k}={v}" for k, v in params.items()])
        html += f"<h4>Parameter: {param_text}</h4>\n"

    bilder = ["step0_PW_vs_Kataster.png", "step4_maxima.png", "Step5_watershed.png"]
    bilder_html = ""
    for bild in bilder:
        bildpfad = os.path.join(ordner_path, bild)
        if os.path.isfile(bildpfad):
            rel_path = os.path.relpath(bildpfad, os.path.dirname(ziel_html))
            bilder_html += f'<img src="{rel_path}" alt="{bild}" style="max-width:500px; max-height:360px; margin:8px;">'

    if bilder_html:
        html += f'<div style="display: flex; flex-direction: row; align-items: flex-start;">{bilder_html}</div><br>'

    html += "<hr>\n"
    return html


def make_html_report(output_dir, ziel_html):
    html = "<html><head><meta charset='utf-8'><title>Segmentierungs-Report</title></head><body>"
    html += "<h1>Segmentierungsergebnisse</h1>\n"

    for ordner in sorted(os.listdir(output_dir)):
        ordner_path = os.path.join(output_dir, ordner)
        if os.path.isdir(ordner_path):
            html += html_for_folder(ordner_path, ordner, ziel_html)

    html += "</body></html>"
    with open(ziel_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML-Report gespeichert: {ziel_html}")


if __name__ == "__main__":
    output_dir = r"C:\Users\marco\Documents\CodeBTh04\arbeitspakete\02_segmentierung\01_Segm_Baeume\output"
    ziel_html = r"C:\Users\marco\Documents\CodeBTh04\arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Resultate\report.html"
    make_html_report(output_dir, ziel_html)
