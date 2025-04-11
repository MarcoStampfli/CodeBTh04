import os

def erstelle_plot_dateinamen(originalname: str, suffix: str) -> str:
    """
    Erzeugt einen neuen standardisierten Plot-Dateinamen auf Basis des Originals.
    Beispiel: Klass_Platte_3_Ausschnitt_1_Bäume_HSV.txt → Klass_P3A1_Bäume_<suffix>.png
    """
    # Entferne "_HSV.txt"
    basename = originalname.replace("_HSV.txt", "")
    
    # Extrahiere den Baum-/Objektnamen (letzter Teil nach dem letzten "_")
    teile = basename.split("_")
    objektname = teile[-1]  # z. B. "Bäume"
    platteNr= teile[2]
    ausNr= teile[4]

    # Erstelle neuen Dateinamen
    neuer_name = f"P{platteNr}A{ausNr}_Klasse_{objektname}_{suffix}.png"
    return neuer_name


def rename_diagramme_dateien(ordner_pfad):
    """
    Erzeugt einen neuen standardisierten Plot-Dateinamen auf Basis des Originals.
    Beispiel: Klass_Platte_3_Ausschnitt_1_Bäume_HSV.txt_Dichteverteilung_XYZ_Norm.png
    Rename:   → P3A1_Klass_Bäume_Dichteverteilung_XYZ_Norm.png
    """
    for dateiname in os.listdir(ordner_pfad):
        if not dateiname.endswith(".png"):
            continue

        # Beispielname: Klass_Platte_3_Ausschnitt_1_Bäume_HSV.txt_Dichteverteilung_XYZ_Norm.png
        alt_path = os.path.join(ordner_pfad, dateiname)

        if "_HSV.txt_" not in dateiname:
            print(f"Wird übersprungen (nicht im erwarteten Format): {dateiname}")
            continue

        # Split am _HSV.txt_ → [prefix mit Baumname, suffix]
        basis, suffix = dateiname.split("_HSV.txt_", 1)  # z. B. Dichteverteilung_XYZ_Norm.png

        # Extrahiere Objektname (letzter Teil vom basis)
        objektname = basis.split("_")[-1]
        platteNr= basis.split("_")[2]
        ausNr= basis.split("_")[4]

        # Erstelle neuen Namen
        neuer_name = f"P{platteNr}A{ausNr}_Klasse_{objektname}_{suffix}"
        neu_path = os.path.join(ordner_pfad, neuer_name)

        os.rename(alt_path, neu_path)
        print(f"Umbenannt: {dateiname} → {neuer_name}")




# Ordner mit den Eingabedateien
# ordner_pfad = "D:\BTh04_Stadtmodel\Diagramme"
ordner_pfad = r"S:\HABG\E1364_IGEO_BTH\E1364_BTH4\06_Auswertung\01_Klassifizierung\00_Datenerkundung\SeabornPlots\Diagramme"

# rename_diagramme_dateien(ordner_pfad=ordner_pfad)

import os

# Specify the directory you want to explore
directory = ordner_pfad

# List all files in the directory
files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
print(files)
# Print the list of files
# for file in files:
#     print(file)
