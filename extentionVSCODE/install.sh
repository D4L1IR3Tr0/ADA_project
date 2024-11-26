#!/bin/bash


mkdir -p ~/.vscode/extensions/ada-language
cp -r * ~/.vscode/extensions/ada-language/
pip install pygls
python server/server.py