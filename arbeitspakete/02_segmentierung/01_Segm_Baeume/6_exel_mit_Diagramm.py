# -*- coding: utf-8 -*-
"""
Automatische Tabellenerstellung aus Ordnerstruktur
mit Einbettung von Bildern und angepasster Zeilenhöhe in Excel (.xlsx)

Voraussetzungen:
- pip install pandas openpyxl pillow
"""
import os
import re
import pandas as pd
import openpyxl
from openpyxl.drawing.image import Image as XLImage

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
        for file in os.listdir(ordner_path):
            if "Parameter_res" in file:
                params = parse_filename(file)
                if params:
                    params['Ordnername'] = ordner
                    # Suche nach zugehöriger CSV-Datei
                    csv_file = None
                    for f in os.listdir(ordner_path):
                        if f.endswith('.csv') and f"RunID_{ordner}" in f:
                            csv_file = os.path.join(ordner_path, f)
                            break
                    params['Trees'] = int(count_csv_rows(csv_file)) if csv_file else 0
                    img_path = os.path.join(ordner_path, 'step0_PW_vs_Kataster.png')
                    params['PW vs Trees'] = img_path if os.path.isfile(img_path) else ''
                    params['Dateiname'] = file
                    data.append(params)
    columns = [
        "PW vs Trees", "Ordnername", "Trees", "res", "min_distance", "sigma", "min_height", "eps",
        "min_samples", "diameter_min", "diameter_max",  "Dateiname"
    ]
    df = pd.DataFrame(data)
    df['Trees'] = df['Trees'].astype(int)
    df = df[columns]
    return df

def write_excel_with_images(df, excel_path, image_column='PW vs Trees', img_width=300, img_height=180):
    df.to_excel(excel_path, index=False)
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    img_col_idx = df.columns.get_loc(image_column) + 1

    row_height_pts = img_height * 0.75  # Umrechnung Pixel zu Punkt (Excel)

    for idx, row in df.iterrows():
        pfad = row[image_column]
        excel_row = idx + 2  # Header ist Zeile 1
        if isinstance(pfad, str) and pfad.lower().endswith(('.png', '.jpg', '.jpeg')) and os.path.isfile(pfad):
            try:
                img = XLImage(pfad)
                img.width = img_width
                img.height = img_height
                cell = ws.cell(row=excel_row, column=img_col_idx)
                ws.add_image(img, cell.coordinate)
                ws.row_dimensions[excel_row].height = row_height_pts
            except Exception as e:
                print(f"Bild konnte nicht eingefügt werden ({pfad}): {e}")

    wb.save(excel_path)
    print(f"Excel mit Bildern und angepasster Zeilenhöhe gespeichert: {excel_path}")

if __name__ == "__main__":
    output_dir = r"C:\Users\marco\Documents\CodeBTh04\arbeitspakete\02_segmentierung\01_Segm_Baeume\output"
    ziel_excel = r"C:\Users\marco\Documents\CodeBTh04\arbeitspakete\02_segmentierung\01_Segm_Baeume\output\Resultate\parameter_tabelle_mit_bildern_final.xlsx"

    df = extract_params_from_output(output_dir)
    write_excel_with_images(df, ziel_excel)
