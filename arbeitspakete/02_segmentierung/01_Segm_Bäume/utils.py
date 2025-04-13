
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_centroid_variants_from_index(txt_path, index_csv_path, res):
    """
    Vergleicht vier Varianten (original, flip_x, flip_y, flip_xy) der Rücktransformation
    von Baumgipfel-Index-Koordinaten zu Weltkoordinaten auf Basis der Punktwolke.
    """
    print("Lade Punktwolke ...")
    df_pts = pd.read_csv(txt_path, delimiter=";", header=None, names=["X", "Y", "Z"])
    df_pts = df_pts[df_pts["Z"] > 2.0]

    # Koordinatenbereich berechnen
    x_min, x_max = df_pts["X"].min(), df_pts["X"].max()
    y_min, y_max = df_pts["Y"].min(), df_pts["Y"].max()

    print("Lade Baumgipfel-Index ...")
    df_idx = pd.read_csv(index_csv_path)  # erwartet Spalten: cy, cx
    local_max = df_idx[["cy", "cx"]].values

    variants = {
        "original": lambda cy, cx: (x_min + cx * res, y_min + cy * res),
        "flip_x":   lambda cy, cx: (x_max - cx * res, y_min + cy * res),
        "flip_y":   lambda cy, cx: (x_min + cx * res, y_max - cy * res),
        "flip_xy":  lambda cy, cx: (x_max - cx * res, y_max - cy * res),
    }

    fig, axs = plt.subplots(2, 2, figsize=(14, 12))
    axs = axs.ravel()

    for i, (name, transform) in enumerate(variants.items()):
        x_coords, y_coords = [], []
        for cy, cx in local_max:
            x, y = transform(cy, cx)
            x_coords.append(x)
            y_coords.append(y)

        axs[i].scatter(df_pts["X"], df_pts["Y"], s=0.2, color='green', label="Punktwolke")
        axs[i].scatter(x_coords, y_coords, s=6, color='orange', label=f"Gipfel ({name})")
        axs[i].set_title(f"Variante: {name}")
        axs[i].set_xlabel("Easting [m]")
        axs[i].set_ylabel("Northing [m]")
        axs[i].axis('equal')
        axs[i].legend()

    plt.suptitle("Vergleich der Rücktransformationen der Baumgipfel", fontsize=16)
    plt.tight_layout()
    plt.show()


def verify_tree_positions(txt_path, csv_path, height_filter=2.0):
    """
    Prüft, ob die Baumkataster-Koordinaten korrekt auf die Punktwolke passen.
    
    txt_path : Pfad zur Punktwolke als .txt mit Spalten X Y Z (Easting, Northing, Höhe)
    csv_path : Pfad zur baumdaten_watershed.csv mit Spalten X, Y
    """
    print("Lade Punktwolke ...")
    df_pts = pd.read_csv(txt_path, delimiter=";", header=None, names=["X", "Y", "Z"])
    df_pts = df_pts[df_pts["Z"] > height_filter]  # nur hohe Punkte anzeigen

    print("Lade Baumdaten ...")
    df_trees = pd.read_csv(csv_path)

    print("Erzeuge Plot ...")
    plt.figure(figsize=(10, 10))
    plt.scatter(df_pts["X"], df_pts["Y"], s=0.2, c='green', label="Punktwolke")
    plt.scatter(df_trees["X"], df_trees["Y"], s=8, c='orange', label="Baumkataster")
    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.legend()
    plt.axis('equal')
    plt.title("Verifikation: Baumkataster über Punktwolke")
    plt.grid(True)
    plt.show()