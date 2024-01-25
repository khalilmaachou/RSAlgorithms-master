from scipy.io import loadmat
import numpy as np
import sys

if len(sys.argv) != 2:
    print("ERROR PLEASE SPECIFY THE MAT FILENAME")

data = loadmat(sys.argv[1])

data_array = data[list(data.keys())[-1]]
print(data_array)

filename = 'ep_ratings.txt'
if data_array.shape[1] == 2: 
    # Créer un tableau de 1 qui a la même longueur que votre tableau original
    ones = np.ones((data_array.shape[0], 1), dtype=np.uint16)

    # Concaténer le tableau de 1 avec votre tableau original
    data_array = np.column_stack((data_array, ones))
    filename = 'ep_trust.txt'

# Ouvrir un fichier texte en mode écriture
with open(filename, 'w') as fichier:
    for paire in data_array:
        # Écrire chaque paire suivi d'un '1'
        ligne = f"{paire[0]} {paire[1]} {paire[3]}\n"
        fichier.write(ligne)

