#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

# Ajouter le chemin de l'application au Python path
sys.path.insert(0, "/var/www/ecowash/")

# Activer l'environnement virtuel
activate_this = '/var/www/ecowash/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Importer l'application Flask
from main import app as application

if __name__ == "__main__":
    application.run()