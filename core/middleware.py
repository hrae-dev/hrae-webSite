"""
Middleware de sécurité et rate limiting pour HRAE

Fonctionnalités:
- Gestion centralisée des erreurs Ratelimited
- Ajout d'en-têtes de rate limiting informatifs
- Logs détaillés des tentatives bloquées
- Détection des patterns d'attaque
"""

from django.shortcuts import render
from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited
import logging

logger = logging.getLogger('django_ratelimit')


class RateLimitMiddleware:
    """
    Middleware pour gérer les exceptions de rate limiting de manière centralisée
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """
        Intercepte les exceptions Ratelimited et retourne une réponse appropriée
        """
        if isinstance(exception, Ratelimited):
            # Logger l'événement avec détails
            logger.warning(
                f"[RATE LIMIT] Blocked request - "
                f"IP: {self.get_client_ip(request)} - "
                f"User: {request.user if request.user.is_authenticated else 'Anonymous'} - "
                f"Path: {request.path} - "
                f"Method: {request.method} - "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )
            
            # Retourner réponse appropriée selon le type de requête
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                # Requête AJAX: retourner JSON
                return JsonResponse({
                    'error': 'rate_limit_exceeded',
                    'message': 'Trop de requêtes. Veuillez réessayer dans quelques minutes.',
                    'status': 429
                }, status=429)
            else:
                # Requête normale: retourner template HTML
                from Home.models import SiteSettings
                settings = SiteSettings.get_settings()
                return render(request, 'errors/429.html', {
                    'settings': settings,
                }, status=429)
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """
        Récupère l'adresse IP réelle du client (même derrière proxy/Nginx)
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Prendre la première IP (la vraie IP du client)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Middleware pour ajouter des en-têtes de sécurité supplémentaires
    (en complément de ceux déjà dans Nginx)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Ajouter des headers de rate limiting informatifs
        if hasattr(response, 'status_code') and response.status_code != 429:
            # Headers informatifs (optionnel, pour debugging)
            response['X-RateLimit-Limit'] = '100'  # Limite par défaut
            response['X-RateLimit-Remaining'] = 'variable'
        
        return response


class AttackDetectionMiddleware:
    """
    Middleware pour détecter les patterns d'attaque suspects
    """
    
    # Patterns suspects dans les URLs
    SUSPICIOUS_PATTERNS = [
        'wp-admin',
        'wp-login',
        'phpmyadmin',
        'admin.php',
        '.env',
        '.git',
        'config.php',
        'shell',
        'eval(',
        'base64_decode',
        '../',
        '..\\',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.security')
        
    def __call__(self, request):
        # Vérifier les patterns suspects
        if self.is_suspicious_request(request):
            self.logger.error(
                f"[ATTACK DETECTED] Suspicious request - "
                f"IP: {self.get_client_ip(request)} - "
                f"Path: {request.path} - "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )
            
            # Option 1: Bloquer la requête (retourner 403)
            # from django.http import HttpResponseForbidden
            # return HttpResponseForbidden("Access Denied")
            
            # Option 2: Laisser passer mais logger (pour analyse)
            # (recommandé pour éviter les faux positifs)
        
        response = self.get_response(request)
        return response
    
    def is_suspicious_request(self, request):
        """
        Vérifie si la requête contient des patterns suspects
        """
        path_lower = request.path.lower()
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in path_lower:
                return True
        
        # Vérifier les User-Agent suspects (bots malveillants)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'masscan', 'nmap', 'dirbuster']
        
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        return False
    
    @staticmethod
    def get_client_ip(request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip