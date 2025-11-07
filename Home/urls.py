from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('about-us/', views.about_us, name='about_us'),

    path('services/', views.our_services, name='our_services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),

    path('team/', views.our_team, name='our_team'),
    path('team/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),

    path('news/', views.news, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),

    path('health-campaigns/', views.health_campaigns, name='health_campaigns'),
    path('health-campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),

    path('partners/', views.our_partners, name='our_partners'),
    path('practical-info/', views.practical_info, name='practical_info'),
    path('contact-us/', views.contact_us, name='contact_us'),
]
