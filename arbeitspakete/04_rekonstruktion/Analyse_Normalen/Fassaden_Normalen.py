import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

input_path = r'arbeitspakete\04_rekonstruktion\Analyse_Normalen\input'
output_path = r'arbeitspakete\04_rekonstruktion\Analyse_Normalen\output'
os.makedirs(output_path, exist_ok=True)
id = 1

# Hilfsfunktion zum Einlesen und Umwandeln
def load_angles(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return [float(line.strip().replace('[', '').replace(']', '')) for line in lines]



# Dateien einlesen
angles1 = load_angles(f'{input_path}/Cloud_1.txt')
angles2 = load_angles(f'{input_path}/Cloud_2.txt')
angles3 = load_angles(f'{input_path}/Cloud_3.txt')

# Statistiken berechnen
def describe(data):
    return np.mean(data), np.std(data)

mean1, std1 = describe(angles1)
mean2, std2 = describe(angles2)
mean3, std3 = describe(angles3)

# KDE-Plot
plt.figure(figsize=(10, 6))

sns.kdeplot(angles1, fill=True, color='red', label=f'Cloud 1 (μ={mean1:.2f}, σ={std1:.2f})', linewidth=1.5)
sns.kdeplot(angles2, fill=True, color='green', label=f'Cloud 2 (μ={mean2:.2f}, σ={std2:.2f})', linewidth=1.5)
sns.kdeplot(angles3, fill=True, color='blue', label=f'Cloud 3 (μ={mean3:.2f}, σ={std3:.2f})', linewidth=1.5)

plt.title('Dichteverteilung der Normalenwinkel')
plt.xlabel('Winkel (Grad)')
plt.ylabel('Dichte')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Diagramm speichern
plt.savefig(os.path.join(output_path, f"winkel_kde_plot_ID_{id}.png"), dpi=300)
plt.show()
