import pandas as pd
import os
import time
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

# Zeitmessung starten
start_time = time.time()

# Ordner mit den Eingabedateien
ordner_pfad = "SeabornPlots\Klass_Platte_3_Ausschnitt_1\HSV_erweitert"

# Liste aller .txt-Dateien im Ordner
dateien = [f for f in os.listdir(ordner_pfad) if f.endswith(".txt")]

output_folder = "Diagramme_clean"
os.makedirs(output_folder, exist_ok=True)

# Progressbar mit tqdm
for dateiname in tqdm(dateien, desc="Verarbeite Dateien"):
    dateipfad = os.path.join(ordner_pfad, dateiname)
    loop_start = time.time()

    klasse = dateiname.split("_")[-2]

    # Datei einlesen
    df = pd.read_csv(dateipfad, delimiter=";", decimal=".", header=None)

    # Spaltennamen setzen
    df.columns = ["X coordinate", "Y coordinate", "Z coordinate",
                  "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)",
                  "X scan dir", "Y scan dir", "Z scan dir", "Hue (°)", "Saturation (%)", "Value (%)"]
    
    # # KDE-Plots für RGB-Werte
    # plt.figure(figsize=(10, 6))
    # sns.kdeplot(df["Red color (0-255)"], label="Rot", color="red", fill=False)
    # sns.kdeplot(df["Green color (0-255)"], label="Grün", color="green", fill=False)
    # sns.kdeplot(df["Blue color (0-255)"], label="Blau", color="blue", fill=False)

    # # Diagramm formatieren
    # plt.title(f"Dichteverteilung der RGB-Werte der Klasse {klasse}")
    # plt.xlabel("Farbwert (0-255)")
    # plt.xlim(0,255)
    # plt.ylabel("Dichte")
    # plt.ylim(0,0.06)
    # plt.legend()
    # file_path = os.path.join(output_folder, dateiname+"_Dichteverteilung_RGB.png")
    # plt.savefig(file_path, dpi=300)
    # plt.close()
    # print(f" RGB-Dichteplot gespeichert: {os.path.basename(file_path)}")    

    # # KDE-Plots für XYZ Normalen-Werte
    # plt.figure(figsize=(10, 6))
    # sns.kdeplot(df["X scan dir"], label="X-Normale", color="red", fill=False)
    # sns.kdeplot(df["Y scan dir"], label="Y-Normale", color="green", fill=False)
    # sns.kdeplot(df["Z scan dir"], label="Z-Normale", color="blue", fill=False)

    # # Diagramm formatieren
    # plt.title(f"Dichteverteilung der XYZ-Normalen der Klasse {klasse}")
    # plt.xlabel("Normalenwert (0-1)")
    # plt.xlim(-1,1)
    # plt.ylabel("Dichte")
    # plt.legend()
    # file_path = os.path.join(output_folder, dateiname+"_Dichteverteilung_XYZ_Norm.png")
    # plt.savefig(file_path, dpi=300)
    # plt.close()
    # print(f" XYZ-Normalenplot gespeichert: {os.path.basename(file_path)}")


    # Optional: Sampling
    # df_sample = df.sample(frac=0.2, random_state=42)
    df_sample = df

    # Reshape: Scan-Daten in ein langes Format bringen
    df_melted = df_sample.melt(
        id_vars=["Hue (°)"], 
        value_vars=["X scan dir", "Y scan dir", "Z scan dir"], # , "Y scan dir", "Z scan dir"
        var_name="Scan-Achse", 
        value_name="Scan-Wert"
    )

    # Plot mit hue für unterschiedliche Achsen
    sns.set_theme(style="ticks")
    g = sns.jointplot(
        data=df_melted,
        x="Hue (°)",
        y="Scan-Wert",
        hue="Scan-Achse",
        kind="kde",
        fill=False
    )
    # Plot speichern
    g.ax_joint.set_xlim(0, 360)     # Für Hue-Werte
    g.ax_joint.set_ylim(-1, 1)      # Für Scan-Werte
    g.figure.suptitle("KDE: Scanrichtung (X/Y/Z) vs. Hue", fontsize=14)
    g.figure.subplots_adjust(top=0.95)  # Platz lassen für den Titel

    g.ax_joint.legend(loc="lower right")

    file_path = os.path.join(output_folder, dateiname + "_KDE_ScanXYZ_vs_hue.png")
    g.figure.savefig(file_path, dpi=300, bbox_inches="tight")
    plt.close(g.figure)
    print(f" Jointplot Scan vs. Hue gespeichert: {os.path.basename(file_path)}")

    # Dauer für diese Datei berechnen
    loop_end = time.time()
    loop_dauer = loop_end - loop_start
    h, r = divmod(loop_dauer, 3600)
    m, s = divmod(r, 60)
    print(f" Dauer für {dateiname}: {int(h):02d}:{int(m):02d}:{int(s):02d} (hh:mm:ss)\n")


# Zeitmessung beenden
end_time = time.time()
dauer = end_time - start_time

stunden, rest = divmod(dauer, 3600)
minuten, sekunden = divmod(rest, 60)

print(f"\n Fertig! Alle Dateien wurden gespeichert.")
print(f" Dauer: {int(stunden):02d}:{int(minuten):02d}:{int(sekunden):02d} (hh:mm:ss)")
