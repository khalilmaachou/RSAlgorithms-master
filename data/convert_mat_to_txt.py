from scipy.io import loadmat
import numpy as np
import sys

if len(sys.argv) != 3:
    print("ERROR PLEASE SPECIFY THE TOW MAT FILENAME")

data_trust = loadmat(sys.argv[1])
data_rating = loadmat(sys.argv[2])

data_array_trust = data_trust[list(data_trust.keys())[-1]]
data_array_rating = data_rating[list(data_rating.keys())[-1]]

#indices = np.random.choice(data_array.shape[0], 5000, replace=False)
#data_array = data_array[indices]

print(data_array_trust.shape)

# Sélectionner n nœuds uniques
noeuds_uniques = np.unique(data_array_trust[:, :2])
noeuds_aleatoires = np.random.choice(noeuds_uniques, 5000, replace=False)

# Filtrer les arêtes pour créer le sous-graphe
data_array_trust = [arete for arete in data_array_trust if arete[0] in noeuds_aleatoires and arete[1] in noeuds_aleatoires]
data_array_rating = [arete for arete in data_array_rating if arete[0] in noeuds_aleatoires]

# Convertir en array NumPy si nécessaire
data_array_trust = np.array(data_array_trust)
data_array_rating = np.array(data_array_rating)

print(data_array_trust.shape, data_array_rating.shape)


# Créer un tableau de 1 qui a la même longueur que votre tableau original
ones = np.ones((data_array_trust.shape[0], 1), dtype=np.uint16)

# Concaténer le tableau de 1 avec votre tableau original
data_array_trust = np.column_stack((data_array_trust, ones))

filename = 'ep_trust.txt'

# Ouvrir un fichier texte en mode écriture
with open(filename, 'w') as fichier:
    for paire in data_array_trust:
        # Écrire chaque paire suivi d'un '1'
        ligne = f"{paire[0]} {paire[1]} {paire[2]}\n"
        fichier.write(ligne)

filename = 'ep_ratings.txt'
# Ouvrir un fichier texte en mode écriture
with open(filename, 'w') as fichier:
    for paire in data_array_rating:
        # Écrire chaque paire suivi d'un '1'
        ligne = f"{paire[0]} {paire[1]} {paire[3]}\n"
        fichier.write(ligne)



