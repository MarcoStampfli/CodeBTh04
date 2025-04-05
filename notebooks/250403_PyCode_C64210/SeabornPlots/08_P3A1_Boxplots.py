import pandas as pd
import matplotlib.pyplot as plt
import os

# Excel-Datei mit den Daten
excel_file = "SeabornPlots\Klassen_Statistiken_gesamt.xlsx"
df = pd.read_excel(excel_file, sheet_name="Alle_Klassen")

# Liste der Spalten für Boxplots
spalten = ["Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
           "X scan dir", "Y scan dir", "Z scan dir",
           "Hue (°)", "Saturation (%)", "Value (%)"]

# Ausgabeordner
output_folder = "Boxplots_Custom"
os.makedirs(output_folder, exist_ok=True)

# Zeichne je Spalte
for spalte in spalten:
    fig, ax = plt.subplots(figsize=(10, 6))

    box_data = []
    positions = []
    labels = []

    for i, klasse in enumerate(df["Klasse"].unique()):
        df_k = df[df["Klasse"] == klasse][spalte].dropna()
        if df_k.empty:
            continue

        stats = df_k.describe()

        # Boxplot-Datenstruktur nach Matplotlib: [min, Q1, median, Q3, max]
        box = {
            "med": stats["mean"],             # wir verwenden den Mean als Linie
            "q1": stats["25%"],
            "q3": stats["75%"],
            "whislo": stats["min"],
            "whishi": stats["max"],
            "fliers": []                      # keine Ausreißer
        }

        box_data.append(box)
        positions.append(i + 1)
        labels.append(klasse)

    # Zeichnen
    ax.bxp(box_data, positions=positions, showmeans=False)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=45)
    ax.set_title(f"Custom Boxplot – {spalte}")
    ax.set_ylabel(spalte)
    plt.tight_layout()

    # Speichern
    name_clean = spalte.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    plot_path = os.path.join(output_folder, f"CustomBoxplot_{name_clean}.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Custom Boxplot gespeichert: {plot_path}")

