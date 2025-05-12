# Convertisseur de Format de Fichier Fixe - Manuel d'utilisation

## Aperçu
Le Convertisseur de Format de Fichier Fixe est un outil qui convertit des fichiers au format de largeur fixe en format CSV en se basant sur un fichier de métadonnées décrivant la structure du fichier d'entrée. L'outil prend en charge trois types de colonnes : dates, valeurs numériques et chaînes de caractères.

## Prérequis
- Python 3.5 ou plus installé sur votre système
- Paquets Python requis (uniquement si utilisation Web ou API) : requirements.txt

## Méthodes d'utilisation

### 1. Utilisation de l'interface Web

1. Lancez l'interface web :
   ```bash
   python fffc_converter/web.py
   ```
2. L'outil démarre et affiche une URL dans la console (généralement http://localhost:7860)
3. Ouvrez l'URL dans votre navigateur web
4. Dans l'interface web :
   - Téléchargez votre fichier de données (format de largeur fixe)
   - Téléchargez votre fichier de métadonnées (format CSV)
   - Cliquez sur "Convertir" pour traiter les fichiers
   - Téléchargez le fichier CSV résultant et le journal d'erreurs (s'il y en a)

### 2. Utilisation de l'API

1. Lancez le serveur API :
   ```bash
   python fffc_converter/web.py
   ```
2. La documentation de l'API sera disponible à l'URL affichée dans la console (généralement http://localhost:7860/?view=api). Suivez les instructions affichées.

### 3. Utilisation directe en Python

1. Importez le convertisseur dans votre code Python :
   ```python
   from fffc_converter.converter import FixedFileFormatConverter
   ```

2. Utilisation de base :
   ```python
   # Initialiser le convertisseur avec le fichier de métadonnées
   converter = FixedFileFormatConverter("chemin/vers/metadata.csv")
   
   # Convertir un fichier
   with open("chemin/vers/input.txt", "r", encoding="utf-8") as input_file:
       for csv_line, error_line in converter.convert(input_file):
           if csv_line:
               # Traiter la ligne CSV
               print(csv_line)
           if error_line:
               # Gérer l'erreur
               print(error_line)
   ```

## Format du fichier de métadonnées
Le fichier de métadonnées doit être un fichier CSV avec les colonnes suivantes :
1. Nom de la colonne
2. Longueur de la colonne
3. Type de colonne (l'un des suivants : "date", "numérique", "chaîne")

Exemple :
```csv
Date de naissance,10,date
Prénom,15,chaîne
Nom de famille,15,chaîne
Poids,5,numérique
```

## Format de Sortie
- Le fichier CSV de sortie :
  - Utilise la virgule (,) comme séparateur
  - Utilise CRLF comme fin de ligne
  - Inclut une ligne d'en-tête avec les noms des colonnes
  - Formate les dates au format JJ/MM/AAAA
  - Supprime les espaces de fin des colonnes de chaînes
  - Échappe correctement les champs contenant des virgules avec des guillemets doubles

## Gestion des Erreurs
- L'outil génère un fichier journal d'erreurs si des problèmes sont rencontrés pendant la conversion
- Les erreurs incluent :
  - Formats de date invalides
  - Valeurs numériques invalides
  - Longueurs de colonnes incorrectes
  - Fichier de métadonnées mal formé

## Encodage des Fichiers
- Tous les fichiers (entrée, métadonnées et sortie) doivent être encodés en UTF-8
- L'outil peut gérer les caractères spéciaux dans les données

## Considérations de Performance
- L'outil est conçu pour gérer de gros fichiers (plusieurs Go)

## Limitations
- L'outil ne prend pas en charge les colonnes de longueur variable
- Toutes les colonnes doivent avoir une largeur fixe comme spécifié dans les métadonnées
- Le format de date dans les fichiers d'entrée doit être AAAA-MM-JJ
- Les valeurs numériques doivent utiliser le point (.) comme séparateur décimal
- Aucun séparateur de milliers n'est autorisé dans les valeurs numériques