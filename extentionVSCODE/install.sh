#!/bin/bash

# Créer la structure de l'extension
mkdir -p ~/.vscode/extensions/ada-language
cp -r * ~/.vscode/extensions/ada-language/

# Installer les dépendances du serveur de langage
pip install pygls

# Démarrer le serveur de langage
python server/server.py