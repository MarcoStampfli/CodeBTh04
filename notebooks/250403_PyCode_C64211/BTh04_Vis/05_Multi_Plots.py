import seaborn as sns
import pandas as pd

# Daten einlesen
file_path = r"SeabornPlots\P3A3_KOO_RGB_HSV_norm.txt"
df = pd.read_csv(file_path, delimiter=";", decimal=".", header=None)
df.columns = ["X coordinate", "Y coordinate", "Z coordinate", 
              "Red color (0-255)", "Green color (0-255)", "Blue color (0-255)", 
              "X scan dir", "Y scan dir", "Z scan dir",
              "Hue (°)", "Saturation (%)", "Value (%)"]

# Optional: Sampling
df_sample = df.sample(frac=0.2, random_state=42)

# Reshape: Scan-Daten in ein langes Format bringen
df_melted = df_sample.melt(
    id_vars=["Hue (°)"], 
    value_vars=["X scan dir","Y scan dir", "Z scan dir"], # , "Y scan dir", "Z scan dir"
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
g.figure.savefig("KDE_Scan_vs_hue.png", dpi=300, bbox_inches="tight")

print("Plot gespeichert!!!")