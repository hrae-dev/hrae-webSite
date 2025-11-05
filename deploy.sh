#!/bin/bash
set -e

echo "🚀 [HRAE] Starting deployment..."

cd /var/www/hrae-webSite || exit

# Pull depuis GitHub
echo "📦 Pulling latest code..."
git config --global --add safe.directory /var/www/hrae-webSite
git pull origin main

# Activer l'environnement virtuel
echo "🧰 Activating virtualenv..."
source venv/bin/activate

# Mettre à jour les dépendances
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Migrer la base de données
echo "🧱 Applying migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Redémarrer gunicorn et nginx
echo "🔁 Restarting services..."
sudo systemctl restart hrae
sudo systemctl reload nginx

echo "✅ Deployment finished successfully!"
