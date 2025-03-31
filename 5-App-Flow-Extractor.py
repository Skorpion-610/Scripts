import re

# Ensemble pour stocker les valeurs uniques extraites de app=""XXX""
valeurs_app = set()

# Ouvrir le fichier CSV
with open('Path/IDXXX.csv', 'r', newline='') as fichier_csv:
    lignes = fichier_csv.readlines()
    
    # Parcourir les lignes du CSV
    for ligne in lignes:
        # Utiliser une expression régulière pour trouver app=""XXX"" où XXX est dynamique
        match = re.search(r'app=""([^"]+)""', ligne)
        if match:
            # Ajouter la valeur entre les guillemets à l'ensemble (ce qui supprime les doublons automatiquement)
            valeurs_app.add(match.group(1))

# Trier les valeurs extraites pour un fichier bien organisé
valeurs_app_triees = sorted(valeurs_app)

# Enregistrer les valeurs dans un fichier texte joliment formaté
with open('Path/ID_XX_Services.txt', 'w', newline='') as fichier_sortie:
    fichier_sortie.write("Liste des services :\n")
    fichier_sortie.write("=======================\n\n")
    for i, valeur in enumerate(valeurs_app_triees, start=1):
        fichier_sortie.write(f"{i}. {valeur}\n")

print(f"Extraction réussie. {len(valeurs_app_triees)} valeurs uniques enregistrées dans 'ID_XXX_Services.txt'.")
