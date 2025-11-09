from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.index, name='home'),

    # À propos
    path('about-us/', views.about_us, name='about'),

    # Services
    path('services/', views.our_services, name='services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),

    # Équipe médicale
    path('team/', views.our_team, name='team'),
    path('team/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    # Actualités
    path('news/', views.news, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),

    # Campagnes de santé
    path('health-campaigns/', views.health_campaigns, name='health_campaigns'),
    path('health-campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),

    # Partenaires
    path('partners/', views.our_partners, name='our_partners'),
    
    # Informations pratiques
    path('practical-info/', views.practical_info, name='practical_info'),
    
    # Contact
    path('contact-us/', views.contact_us, name='contact'),
    
    # Rendez-vous
    path('appointment/', views.appointment_create, name='appointment'),
    path('appointment/success/', views.appointment_success, name='appointment_success'),
]