
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import os

def zeit(start, stop=None, msg=str("")):
    """
    Rechnet Prozesszeiten aus und macht ein Console-Log

    Parameter:
    start = start der Zeitmessung
    stop = time.time() "aktuelle Zeit" wenn nicht sonnst definiert
    msg = str mit Log-text
    """
    if stop is None:
        stop = time.time()
    elapsed_time = stop - start
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    print(f"{msg}Dauer: {minutes} Minuten und {seconds:.2f} Sekunden")
    return stop

import os
import pandas as pd
import matplotlib.pyplot as plt

def verify_tree_positions2(output_dir, txt_path, csv_path, height_filter=int(4), filename="step0_PW_vs_Kataster.png"):
    """
    Prüft, ob die Baumkataster-Koordinaten korrekt auf die Punktwolke passen,
    und entfernt die numerischen Achsenbeschriftungen.

    Parameter:
    output_dir     : Zielordner zum Speichern
    txt_path       : Pfad zur Punktwolke als .txt mit Spalten X Y Z (Easting, Northing, Höhe)
    csv_path       : Pfad zur baumdaten_watershed.csv mit Spalten ID E N H DM
    height_filter  : nur hohe Punkte anzeigen (Visualisierung)
    filename       : Name der Ausgabedatei (PNG)
    """
    print("Lade Punktwolke ...")
    df_pts = pd.read_csv(txt_path, delimiter=";", header=None, names=["X", "Y", "Z"])
    df_pts = df_pts[df_pts["Z"] > height_filter]  # nur hohe Punkte anzeigen

    print("Lade Baumdaten ...")
    df_trees = pd.read_csv(csv_path, delimiter=",", header=0,
                           names=["Tree_ID", "E", "N", "Height_m", "Crown_Diameter_m"])
    
    fontsize = 18
    pad_inches = fontsize / 72 / 2

    print("Erzeuge Plot ...")
    plt.figure(figsize=(14, 10))
    plt.scatter(df_pts["X"], df_pts["Y"], s=0.2, c='green', label="Punktwolke")
    plt.scatter(df_trees["E"], df_trees["N"], s=12, c='orange', label="Baumkataster")
    # plt.xlabel("Easting [m]")
    # plt.ylabel("Northing [m]")
    plt.legend()
    plt.axis('equal') # 'equal'
    plt.title("Verifikation: Baumkataster über Punktwolke", fontsize=fontsize)
    plt.grid(False)

    # Entferne die numerischen Achsenbeschriftungen
    plt.xticks([])  # X-Tick-Labels ausblenden
    plt.yticks([])  # Y-Tick-Labels ausblenden

    # … nach plt.grid(False) und vor plt.savefig …
    plt.tight_layout()  # passt alle Ränder an

    # Plot speichern und Weißraum um das Bild herum abschneiden
    file_path = os.path.join(output_dir, filename)
    plt.savefig(
        file_path,
        dpi=300,
        bbox_inches='tight',  # schneidet außen rum alles weg
        pad_inches=pad_inches          # Abstand zum Bild auf null setzen
    )
    plt.close()



def verify_tree_positions(output_dir, txt_path, csv_path, height_filter=int(4)):
    """
    Prüft, ob die Baumkataster-Koordinaten korrekt auf die Punktwolke passen.

    Parameter:
    output_dir : Zielordner zum speichern
    txt_path : Pfad zur Punktwolke als .txt mit Spalten X Y Z (Easting, Northing, Höhe)
    csv_path : Pfad zur baumdaten_watershed.csv mit Spalten ID E N H DM
    height_filter : nur hohe Punkte anzeigen (Visualisierung)
    """
    print("Lade Punktwolke ...")
    df_pts = pd.read_csv(txt_path, delimiter=";", header=None, names=["X", "Y", "Z"])
    df_pts = df_pts[df_pts["Z"] > height_filter]  # nur hohe Punkte anzeigen

    print("Lade Baumdaten ...")
    df_trees = pd.read_csv(csv_path, delimiter=",",header=0,names=["Tree_ID","E","N","Height_m","Crown_Diameter_m"])

    print("Erzeuge Plot ...")
    plt.figure(figsize=(10, 10))
    plt.scatter(df_pts["X"], df_pts["Y"], s=0.2, c='green', label="Punktwolke")
    plt.scatter(df_trees["E"], df_trees["N"], s=8, c='orange', label="Baumkataster")
    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.legend()
    plt.axis('equal')
    plt.title("Verifikation: Baumkataster über Punktwolke")
    plt.grid(False)
    file_path = os.path.join(output_dir, "step0_PW_vs_Kataster.png")
    plt.savefig(file_path, dpi=300)
    # plt.show()
    plt.close()


def visualize_processing_steps(filtered_points, filtered_labels, chm, chm_smooth, local_max, labels_ws, output_dir, df=None, x_min=None, x_max=None, y_min=None, y_max=None, res=1, RunID=""):
    """
    Erstellt und speichert Visualisierungen der wichtigsten Prozessschritte:
    1. Punktwolke
    2. DBSCAN-Cluster
    3. CHM
    4. Lokale Maxima
    5. Watershed-Segmente
    6. Small Multiples (alle Schritte nebeneinander)
    7. CHM + Baumgipfel farbcodiert nach Kronendurchmesser (optional, wenn df übergeben wird)
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    from skimage.color import label2rgb

    # -------- 1. Punktwolke --------
    fig1 = plt.figure(figsize=(6, 5))
    plt.scatter(filtered_points[:, 0], filtered_points[:, 1], c=filtered_points[:, 2], cmap='viridis', s=1)
    plt.title("1. Gefilterte Punktwolke")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.colorbar(label='Höhe [m]')
    plt.tight_layout()
    step1_path = os.path.join(output_dir, "step1_pointcloud.png")
    plt.savefig(step1_path, dpi=200)
    plt.close()
    print(f"Punktwolke gespeichert: {step1_path}")

    # -------- 2. DBSCAN Clustering --------
    fig2 = plt.figure(figsize=(6, 5))
    if len(filtered_labels) == len(filtered_points):
        plt.scatter(filtered_points[:, 0], filtered_points[:, 1], c=filtered_labels, cmap='tab20', s=1)
    else:
        plt.scatter(filtered_points[:, 0], filtered_points[:, 1], c='gray', s=1)
        print("[WARNUNG] Clusterlabels stimmen nicht mit Punktanzahl überein – Darstellung in Grau.")
    plt.title("2. DBSCAN-Clustering")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    step2_path = os.path.join(output_dir, "step2_dbscan.png")
    plt.savefig(step2_path, dpi=200)
    plt.close()
    print(f"DBSCAN gespeichert: {step2_path}")

    # -------- 3. CHM --------
    fig3 = plt.figure(figsize=(6, 5))
    plt.imshow(chm.T, cmap='terrain', origin='lower')
    plt.title("3. Canopy Height Model (CHM)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.colorbar(label='Höhe [m]')
    plt.tight_layout()
    step3_path = os.path.join(output_dir, "step3_chm.png")
    plt.savefig(step3_path, dpi=200)
    plt.close()
    print(f"CHM gespeichert: {step3_path}")

    # -------- 4. Lokale Maxima --------
    fig4 = plt.figure(figsize=(6, 5))
    plt.imshow(chm_smooth.T, cmap='terrain', origin='lower')
    lx = local_max[:, 0]
    ly = local_max[:, 1]
    plt.scatter(lx, ly, c='red', s=2)
    plt.title("4. Lokale Maxima im CHM")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    step4_path = os.path.join(output_dir, "step4_maxima.png")
    plt.savefig(step4_path, dpi=200)
    plt.close()
    print(f"Maxima gespeichert: {step4_path}")

    # -------- 5. Watershed Segmente --------
    fig5 = plt.figure(figsize=(6, 5))
    plt.imshow(label2rgb(labels_ws.T, bg_label=0), origin='lower')
    plt.title("5. Watershed-Segmente")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    step5_path = os.path.join(output_dir, "step5_watershed.png")
    plt.savefig(step5_path, dpi=200)
    plt.close()
    print(f"Segmente gespeichert: {step5_path}")

    # -------- 6. Small Multiples --------
    fig, axes = plt.subplots(1, 5, figsize=(25, 5))
    step_files = [
        ("step1_pointcloud.png", "Punktwolke"),
        ("step2_dbscan.png", "DBSCAN"),
        ("step3_chm.png", "CHM"),
        ("step4_maxima.png", "Maxima"),
        ("step5_watershed.png", "Segmente")
    ]
    for ax, (filename, title) in zip(axes, step_files):
        img = plt.imread(os.path.join(output_dir, filename))
        ax.imshow(img)
        ax.set_title(title, fontsize=10)
        ax.axis('off')

    plt.tight_layout()
    all_path = os.path.join(output_dir, "step_all_small_multiples.png")
    plt.savefig(all_path, dpi=200)
    plt.close()
    print(f"Small Multiples gespeichert: {all_path}")

        # -------- 7. CHM mit Baumgipfeln (Durchmesserfarben) --------
    if df is not None and x_min is not None and y_min is not None:
        print("Visualisiere CHM + Baumgipfel (farblich nach Kronendurchmesser) ...")
        fig7 = plt.figure(figsize=(10, 8))
        plt.imshow(chm.T, cmap='viridis', origin='lower', extent=[y_min, y_max, x_min, x_max])

        x_coords = x_min + local_max[:, 1] * res
        y_coords = y_min + local_max[:, 0] * res
        max_labels = labels_ws[local_max[:, 0], local_max[:, 1]]

        diameters = []
        for lbl in max_labels:
            entry = df[df["Tree_ID"] == lbl]
            if not entry.empty:
                diameters.append(entry["Crown_Diameter_m"].values[0])
            else:
                diameters.append(np.nan)

        diameters = np.array(diameters)
        sc = plt.scatter(y_coords, x_coords, c=diameters, cmap='Greens', s=20, edgecolor='k', label="Baumgipfel")
        plt.colorbar(sc, label='Durchmesser Baumkrone [m]')
        plt.title("CHM mit Baumgipfeln (farbcodiert nach Kronendurchmesser)")
        plt.legend()
        fig7_path = os.path.join(output_dir, f"chm_baumgipfel_colordiameter_RunID_{RunID}.png")
        plt.savefig(fig7_path, dpi=300)
        plt.close()
        print(f"CHM gespeichert: {fig7_path}")

    print("Alle Visualisierungen erfolgreich gespeichert.")
