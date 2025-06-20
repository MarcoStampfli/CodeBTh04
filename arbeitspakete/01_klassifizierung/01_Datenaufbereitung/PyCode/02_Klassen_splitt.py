import pandas as pd
import os
# ================================================================
# Beschreibung:     BTH 04 - Rekonstruktion Stadtmodell Basel 1960
# Erstellt mit:     Unterstützung durch ChatGPT (OpenAI)
# Version:          GPT-4, Juni 2025
# Autor:            Marco Stampfli und Vania Fernandes Pereira
# ================================================================

# Datei mit Clustering-Ergebnissen laden
file_path = "PW_8_Klassen.txt"  # Falls der Name anders ist, bitte anpassen
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)

# Spaltennamen setzen basierend auf der bestehenden Datei
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)", "Color Cluster"]

# Erstelle einen Ordner für die Ausgabe (falls nicht vorhanden)
output_folder = "Clustered_Files"
os.makedirs(output_folder, exist_ok=True)

# Daten in separate Dateien je Klasse speichern
for cluster_id in df["Color Cluster"].unique():
    # Filtere die Punkte für die aktuelle Klasse
    cluster_df = df[df["Color Cluster"] == cluster_id]

    # Dateiname für die Klasse
    output_file = os.path.join(output_folder, f"PW_Klasse_{int(cluster_id)}.txt")

    # Speichern ohne Header
    cluster_df.to_csv(output_file, sep=";", index=False, decimal=".", header=False)

    print(f"Datei gespeichert: {output_file}")

print("Alle Cluster-Dateien wurden erfolgreich erstellt!")

# Bestätigung durch Anzeige einer der generierten Dateien
# import ace_tools as tools
# tools.display_dataframe_to_user(name="Beispiel Cluster-Daten", dataframe=cluster_df)
