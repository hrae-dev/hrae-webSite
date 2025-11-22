from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.index, name='home'),

    # À propos
    path('a-propos/', views.about_us, name='about'),

    # Services
    path('services/', views.our_services, name='services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),

    # Équipe médicale
    path('equipe/', views.our_team, name='team'),
    path('equipe/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    # Actualités
    path('actualites/', views.news, name='news'),
    path('actualites/<int:news_id>/', views.news_detail, name='news_detail'),

    # Campagnes de santé
    path('campagnes/', views.health_campaigns, name='health_campaigns'),
    path('campagnes/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),

    # Partenaires
    path('partenaires/', views.our_partners, name='our_partners'),
    
    # Témoignages
    path('temoignages/', views.testimonials_list, name='testimonials'),
    
    # Informations pratiques
    path('informations-pratiques/', views.practical_info, name='practical_info'),
    
    # Contact
    path('contact/', views.contact_us, name='contact_us'),
    path('contact/', views.contact_us, name='contact'),  # Alias pour base.html
    
    # Rendez-vous
    path('rendez-vous/', views.appointment_create, name='appointment'),
    path('rendez-vous/', views.appointment_create, name='appointment_create'),  # Alias pour compatibilité
    path('rendez-vous/confirmation/', views.appointment_success, name='appointment_success'),
    
    # API AJAX
    path('api/staff-by-service/', views.get_staff_by_service, name='api_staff_by_service'),
]