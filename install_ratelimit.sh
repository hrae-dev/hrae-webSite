#!/bin/bash

# ================================================
# HRAE - Script d'installation Rate Limiting
# Installation automatique Redis + Configuration complète
# ================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Vérifier si on est root ou sudo
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Ce script doit être exécuté avec sudo ou en tant que root"
        exit 1
    fi
}

# ================================================
# ÉTAPE 1: Vérifications préalables
# ================================================
print_header "ÉTAPE 1: Vérifications préalables"

check_root

# Vérifier distribution Linux
if ! command -v apt-get &> /dev/null; then
    print_error "Ce script est conçu pour Ubuntu/Debian avec apt-get"
    exit 1
fi

print_success "Système compatible détecté"

# Récupérer le chemin du projet
read -p "Chemin complet vers le projet Django (ex: /var/www/hrae): " PROJECT_DIR

if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Le répertoire $PROJECT_DIR n'existe pas"
    exit 1
fi

print_success "Projet trouvé: $PROJECT_DIR"

# Récupérer l'utilisateur du projet
read -p "Utilisateur propriétaire du projet (ex: www-data ou votre user): " PROJECT_USER

if ! id "$PROJECT_USER" &>/dev/null; then
    print_error "L'utilisateur $PROJECT_USER n'existe pas"
    exit 1
fi

print_success "Utilisateur configuré: $PROJECT_USER"


# ================================================
# ÉTAPE 2: Installation Redis
# ================================================
print_header "ÉTAPE 2: Installation Redis"

if command -v redis-server &> /dev/null; then
    print_warning "Redis est déjà installé"
    redis-server --version
else
    print_info "Installation de Redis..."
    apt-get update
    apt-get install -y redis-server
    print_success "Redis installé avec succès"
fi

# Configuration Redis
print_info "Configuration de Redis..."

# Backup de la config originale
if [ -f /etc/redis/redis.conf ]; then
    cp /etc/redis/redis.conf /etc/redis/redis.conf.backup.$(date +%Y%m%d_%H%M%S)
    print_success "Backup de redis.conf créé"
fi

# Configuration pour production
cat > /etc/redis/redis.conf.d/hrae.conf << 'EOF'
# Configuration Redis pour HRAE

# Bind sur localhost uniquement (sécurité)
bind 127.0.0.1

# Port par défaut
port 6379

# Activer persistence (optionnel mais recommandé)
save 900 1
save 300 10
save 60 10000

# Limites mémoire
maxmemory 256mb
maxmemory-policy allkeys-lru

# Logs
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300

# Snapshots
dbfilename dump.rdb
dir /var/lib/redis
EOF

print_success "Configuration Redis créée"

# Optionnel: Configurer un mot de passe Redis
read -p "Voulez-vous configurer un mot de passe Redis? (recommandé en production) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -sp "Entrez le mot de passe Redis: " REDIS_PASSWORD
    echo
    echo "requirepass $REDIS_PASSWORD" >> /etc/redis/redis.conf.d/hrae.conf
    print_success "Mot de passe Redis configuré"
    REDIS_URL="redis://:$REDIS_PASSWORD@127.0.0.1:6379/1"
else
    REDIS_URL="redis://127.0.0.1:6379/1"
fi

# Redémarrer Redis
systemctl restart redis-server
systemctl enable redis-server

# Vérifier que Redis fonctionne
if redis-cli ping | grep -q "PONG"; then
    print_success "Redis fonctionne correctement"
else
    print_error "Redis ne répond pas"
    exit 1
fi


# ================================================
# ÉTAPE 3: Installation packages Python
# ================================================
print_header "ÉTAPE 3: Installation packages Python"

cd "$PROJECT_DIR"

# Activer l'environnement virtuel si existe
if [ -d "venv" ]; then
    print_info "Activation de l'environnement virtuel..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    print_info "Activation de l'environnement virtuel..."
    source .venv/bin/activate
else
    print_warning "Aucun environnement virtuel trouvé. Installation système."
fi

print_info "Installation des packages Python..."

pip install --upgrade pip
pip install django-ratelimit==4.1.0
pip install django-axes==6.1.1
pip install redis==5.0.1
pip install django-redis==5.4.0

print_success "Packages Python installés"


# ================================================
# ÉTAPE 4: Configuration Django
# ================================================
print_header "ÉTAPE 4: Configuration Django"

# Créer le dossier logs
mkdir -p "$PROJECT_DIR/logs"
chown -R $PROJECT_USER:$PROJECT_USER "$PROJECT_DIR/logs"
chmod 755 "$PROJECT_DIR/logs"
print_success "Dossier logs créé"

# Créer le dossier templates/errors
mkdir -p "$PROJECT_DIR/templates/errors"
chown -R $PROJECT_USER:$PROJECT_USER "$PROJECT_DIR/templates"
print_success "Dossier templates/errors créé"

# Backup settings.py
if [ -f "$PROJECT_DIR/core/settings.py" ]; then
    cp "$PROJECT_DIR/core/settings.py" "$PROJECT_DIR/core/settings.py.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Backup de settings.py créé"
fi

# Mettre à jour .env avec REDIS_URL
if [ -f "$PROJECT_DIR/.env" ]; then
    if grep -q "REDIS_URL" "$PROJECT_DIR/.env"; then
        sed -i "s|REDIS_URL=.*|REDIS_URL=$REDIS_URL|" "$PROJECT_DIR/.env"
    else
        echo "REDIS_URL=$REDIS_URL" >> "$PROJECT_DIR/.env"
    fi
    print_success ".env mis à jour avec REDIS_URL"
else
    print_warning "Fichier .env non trouvé. Créez-le manuellement."
fi


# ================================================
# ÉTAPE 5: Migrations Django
# ================================================
print_header "ÉTAPE 5: Migrations Django"

cd "$PROJECT_DIR"
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

print_success "Migrations Django terminées"


# ================================================
# ÉTAPE 6: Test de configuration
# ================================================
print_header "ÉTAPE 6: Tests de configuration"

# Test Redis depuis Django
print_info "Test de connexion Redis depuis Django..."

python << EOF
import os
import sys
import django

# Setup Django
sys.path.insert(0, '$PROJECT_DIR')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.cache import cache

# Test cache
try:
    cache.set('test_key', 'test_value', 30)
    value = cache.get('test_key')
    if value == 'test_value':
        print("✓ Cache Redis fonctionne!")
    else:
        print("✗ Erreur cache Redis")
        sys.exit(1)
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Redis fonctionne avec Django"
else
    print_error "Problème avec Redis et Django"
    exit 1
fi


# ================================================
# ÉTAPE 7: Configuration Nginx (optionnel)
# ================================================
print_header "ÉTAPE 7: Configuration Nginx"

read -p "Voulez-vous configurer Nginx maintenant? [y/N]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    
    if ! command -v nginx &> /dev/null; then
        print_info "Installation de Nginx..."
        apt-get install -y nginx
        print_success "Nginx installé"
    fi
    
    read -p "Nom de domaine du site (ex: hrae.cm): " DOMAIN_NAME
    
    print_info "Créez le fichier Nginx manuellement:"
    print_info "  1. Copier nginx_hrae_complete.conf vers /etc/nginx/sites-available/$DOMAIN_NAME"
    print_info "  2. Modifier les chemins et domaines dans le fichier"
    print_info "  3. Créer le lien: ln -s /etc/nginx/sites-available/$DOMAIN_NAME /etc/nginx/sites-enabled/"
    print_info "  4. Tester: nginx -t"
    print_info "  5. Recharger: systemctl reload nginx"
    
else
    print_info "Configuration Nginx ignorée"
fi


# ================================================
# ÉTAPE 8: Redémarrage services
# ================================================
print_header "ÉTAPE 8: Redémarrage des services"

# Redémarrer Gunicorn/uWSGI (adapter selon ton setup)
if systemctl is-active --quiet gunicorn; then
    systemctl restart gunicorn
    print_success "Gunicorn redémarré"
elif systemctl is-active --quiet uwsgi; then
    systemctl restart uwsgi
    print_success "uWSGI redémarré"
else
    print_warning "Service WSGI non trouvé. Redémarrez-le manuellement."
fi


# ================================================
# RÉSUMÉ FINAL
# ================================================
print_header "INSTALLATION TERMINÉE !"

echo -e "\n${GREEN}✓ Redis installé et configuré${NC}"
echo -e "${GREEN}✓ Packages Python installés${NC}"
echo -e "${GREEN}✓ Configuration Django mise à jour${NC}"
echo -e "${GREEN}✓ Migrations appliquées${NC}"

echo -e "\n${YELLOW}PROCHAINES ÉTAPES:${NC}"
echo -e "1. Vérifier settings.py et ajouter les configurations manquantes"
echo -e "2. Copier le nouveau views.py avec les décorateurs @ratelimit"
echo -e "3. Copier le middleware personnalisé dans core/middleware.py"
echo -e "4. Ajouter les middleware dans settings.py MIDDLEWARE"
echo -e "5. Copier le template errors/429.html"
echo -e "6. Configurer Nginx avec le fichier fourni"
echo -e "7. Tester le rate limiting sur une URL"

echo -e "\n${BLUE}COMMANDES UTILES:${NC}"
echo -e "  Vérifier Redis: ${YELLOW}redis-cli ping${NC}"
echo -e "  Logs Redis: ${YELLOW}tail -f /var/log/redis/redis-server.log${NC}"
echo -e "  Logs Django: ${YELLOW}tail -f $PROJECT_DIR/logs/ratelimit.log${NC}"
echo -e "  Vider cache: ${YELLOW}redis-cli FLUSHALL${NC}"
echo -e "  Stats Redis: ${YELLOW}redis-cli INFO${NC}"

echo -e "\n${GREEN}Installation réussie! 🎉${NC}\n"