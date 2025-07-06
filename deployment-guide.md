# Guide de Déploiement - EcoWash sur Apache

## Structure des fichiers sur le serveur

```
/var/www/ecowash/
├── main.py                     # Application Flask
├── app.wsgi                    # Configuration WSGI
├── requirements.txt            # Dépendances Python
├── intervalleConfiance.xlsx    # Fichier de configuration
├── recette/                    # Dossier des recettes Excel
│   ├── EcoWash - 1B.xlsx
│   ├── EcoWash - base.xlsx
│   └── EcoWash - bis.xlsx
├── calculations.db             # Base de données SQLite
├── .env                        # Variables d'environnement
├── venv/                       # Environnement virtuel Python
└── dist/                       # Build de l'application Vue.js
    ├── index.html
    ├── assets/
    └── ...
```

## Étapes de déploiement

### 1. Préparation du serveur

```bash
# Installer les modules Apache nécessaires
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod wsgi
sudo a2enmod headers

# Créer le dossier de l'application
sudo mkdir -p /var/www/ecowash
sudo chown -R www-data:www-data /var/www/ecowash
```

### 2. Déploiement du backend (Flask)

```bash
# Copier les fichiers Python
sudo cp main.py /var/www/ecowash/
sudo cp app.wsgi /var/www/ecowash/
sudo cp requirements.txt /var/www/ecowash/
sudo cp intervalleConfiance.xlsx /var/www/ecowash/
sudo cp -r recette/ /var/www/ecowash/

# Créer l'environnement virtuel
cd /var/www/ecowash
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# Configurer les variables d'environnement
sudo cp .env.example .env
sudo nano .env  # Éditer avec vos vraies valeurs
```

### 3. Build et déploiement du frontend (Vue.js)

```bash
# Sur votre machine de développement
cd mon-projet-vue
npm run build

# Copier le build sur le serveur
scp -r dist/ user@your-server:/var/www/ecowash/
```

### 4. Configuration Apache

```bash
# Copier la configuration Apache
sudo cp apache-config.conf /etc/apache2/sites-available/v17.spring-coating.com.conf

# Activer le site
sudo a2ensite v17.spring-coating.com.conf
sudo a2dissite 000-default.conf  # Désactiver le site par défaut

# Redémarrer Apache
sudo systemctl restart apache2
```

### 5. Permissions et sécurité

```bash
# Définir les bonnes permissions
sudo chown -R www-data:www-data /var/www/ecowash
sudo chmod -R 755 /var/www/ecowash
sudo chmod 644 /var/www/ecowash/.env
sudo chmod 600 /var/www/ecowash/calculations.db

# Créer la base de données si elle n'existe pas
cd /var/www/ecowash
sudo -u www-data python3 -c "from main import init_db; init_db()"
```

## Configuration SSL

Pour obtenir un certificat SSL gratuit avec Let's Encrypt :

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-apache

# Obtenir le certificat
sudo certbot --apache -d v17.spring-coating.com

# Le certificat sera automatiquement configuré dans Apache
```

## Variables d'environnement de production

Créez le fichier `/var/www/ecowash/.env` avec :

```env
# Configuration Email
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-application

# Configuration Backend
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# Configuration Base de données
DATABASE_PATH=/var/www/ecowash/calculations.db
```

## Test de l'installation

1. **Test du frontend** : Accédez à `https://v17.spring-coating.com`
2. **Test de l'API** : Vérifiez que `https://v17.spring-coating.com/api/recette` retourne la liste des recettes
3. **Test complet** : Effectuez un calcul depuis l'interface web

## Maintenance

### Logs Apache
```bash
# Voir les erreurs
sudo tail -f /var/log/apache2/ecowash_error.log

# Voir les accès
sudo tail -f /var/log/apache2/ecowash_access.log
```

### Mise à jour de l'application
```bash
# Backend
sudo cp nouveau_main.py /var/www/ecowash/main.py
sudo systemctl reload apache2

# Frontend
npm run build
scp -r dist/ user@your-server:/var/www/ecowash/
```

### Sauvegarde de la base de données
```bash
# Créer une sauvegarde
sudo cp /var/www/ecowash/calculations.db /var/backups/calculations_$(date +%Y%m%d).db
```