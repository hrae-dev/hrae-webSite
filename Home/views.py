from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
import django_ratelimit
from .models import (
    SiteSettings, PatientJourneySection, Page, Service, Staff, Article, Category,
    Campaign, Partner, Appointment, ContactMessage, Testimonial, DirectionMember
)
from .forms import AppointmentForm, CampaignRegistrationForm, ContactMessageForm

from itertools import chain
from django_ratelimit.decorators import ratelimit
import logging
logger = logging.getLogger(__name__)


# ========================================
# 🛡️ GESTION DES ERREURS RATE LIMIT
# ========================================
def rate_limit_exceeded(request, exception=None):
    """
    Vue personnalisée appelée quand un utilisateur dépasse les limites.
    Retourne une page 429 élégante avec informations.
    """
    # Logger l'événement
    logger.warning(
        f"Rate limit exceeded - IP: {request.META.get('REMOTE_ADDR')} - "
        f"Path: {request.path} - User: {request.user if request.user.is_authenticated else 'Anonymous'}"
    )
    
    settings = SiteSettings.get_settings()
    return render(request, 'errors/429.html', {
        'settings': settings,
    }, status=429)

def index(request):
    # Services pour page d'accueil (max 6)
    homepage_services = Service.objects.filter(
        is_active=True,
        show_on_homepage=True
    ).order_by('display_order')[:6]
    
    # Publications récentes (articles + campagnes)
    recent_articles = Article.objects.filter(
        status='published',
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:3]
    
    active_campaigns = Campaign.objects.filter(
        status='active',
        start_date__lte=timezone.now()
    ).order_by('-start_date')[:3]
    
    publications = sorted(
        list(recent_articles) + list(active_campaigns),
        key=lambda x: getattr(x, 'published_at', None) or getattr(x, 'start_date', None),
        reverse=True
    )[:6]
    
    # Chiffres clés depuis SiteSettings
    settings = SiteSettings.get_settings()
    
    context = {
        'homepage_services': homepage_services,
        'publications': publications,
        'settings': settings,
    }
    
    return render(request, 'Home/index.html', context)

def practical_info(request):
    """
    Vue pour la page Espace Patient
    """
    settings = SiteSettings.get_settings()

    # Récupérer la page statique si elle existe
    try:
        page = Page.objects.get(slug='espace-patient', is_active=True)
    except Page.DoesNotExist:
        page = None

    # Récupérer les sections du parcours patient avec leurs étapes
    patient_journey_sections = PatientJourneySection.objects.filter(
        is_active=True
    ).prefetch_related('steps').order_by('display_order')

    context = {
        'settings': settings,
        'page': page,
        'patient_journey_sections': patient_journey_sections,
    }

    return render(request, 'Home/practical_info.html', context)

def about_us(request):
    """Page À propos"""
    settings = SiteSettings.get_settings()
    page = Page.objects.filter(slug='a-propos', is_active=True).first()
    direction_members = DirectionMember.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'page': page,
        'direction_members': direction_members,
    }
    return render(request, 'Home/about_us.html', context)

def our_services(request):
    """Liste des services médicaux"""
    settings = SiteSettings.get_settings()
    
    # Get all active services
    services_list = Service.objects.filter(is_active=True)
    
    # Search filter
    search = request.GET.get('search')
    if search:
        services_list = services_list.filter(
            Q(name__icontains=search) | 
            Q(short_description__icontains=search) |
            Q(full_description__icontains=search) |
            Q(pathologies__icontains=search)
        )
    
    # Pagination (12 services per page)
    paginator = Paginator(services_list, 12)
    page_number = request.GET.get('page', 1)
    services = paginator.get_page(page_number)
    
    context = {
        'settings': settings,
        'services': services,
    }
    return render(request, 'Home/services.html', context)


from django.core.paginator import Paginator
def our_team(request):
    """Liste du personnel médical"""
    settings = SiteSettings.get_settings()
    
    # Filtres
    service_id = request.GET.get('service')
    grade = request.GET.get('grade')
    search = request.GET.get('search')
    
    # Chefs de service (pour le carousel)
    chiefs = Staff.objects.filter(is_visible=True, is_chief=True)[:3]
    
    # Personnel médical (excluant les chefs)
    staff_list = Staff.objects.filter(is_visible=True, is_chief=False).order_by('last_name')
    
    if service_id:
        staff_list = staff_list.filter(services__id=service_id)
    if grade:
        staff_list = staff_list.filter(grade=grade)
    if search:
        staff_list = staff_list.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) | 
            Q(speciality__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(staff_list, 10)
    page_number = request.GET.get('page', 1)
    staff = paginator.get_page(page_number)
    
    services = Service.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'chiefs': chiefs,
        'staff': staff,
        'services': services,
        'grades': Staff.GRADE_CHOICES,
    }
    return render(request, 'Home/team.html', context)

def news(request):
    """Liste des actualités et campagnes avec filtres et pagination"""
    settings = SiteSettings.get_settings()
    today = timezone.now().date()
    
    # Filtres
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    # Campagnes
    campaigns_qs = Campaign.objects.all().order_by('-start_date')
    if search:
        campaigns_qs = campaigns_qs.filter(Q(title__icontains=search) | Q(full_description__icontains=search))
    
    # Articles
    articles_qs = Article.objects.filter(status='published').order_by('-published_at')
    if category_id:
        articles_qs = articles_qs.filter(category_id=category_id)
    if search:
        articles_qs = articles_qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
    
    # Pagination séparée
    campaigns_paginator = Paginator(campaigns_qs, 9)
    articles_paginator = Paginator(articles_qs, 5)
    
    campaigns_page = request.GET.get('campaigns_page', 1)
    articles_page = request.GET.get('articles_page', 1)
    
    campaigns = campaigns_paginator.get_page(campaigns_page)
    articles = articles_paginator.get_page(articles_page)
    
    categories = Category.objects.all()
    
    context = {
        'settings': settings,
        'campaigns': campaigns,
        'articles': articles,
        'categories': categories,
    }
    return render(request, 'news/news.html', context)

def health_campaigns(request):
    """Liste des campagnes groupées par statut"""
    settings = SiteSettings.get_settings()
    today = timezone.now().date()
    
    # Calculer automatiquement le statut basé sur les datesn
    campaigns_ongoing = Campaign.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-start_date')
    
    campaigns_upcoming = Campaign.objects.filter(
        start_date__gt=today
    ).order_by('start_date')
    
    campaigns_completed = Campaign.objects.filter(
        end_date__lt=today
    ).order_by('-end_date')
    
    context = {
        'settings': settings,
        'campaigns_ongoing': campaigns_ongoing,
        'campaigns_upcoming': campaigns_upcoming,
        'campaigns_completed': campaigns_completed,
    }
    return render(request, 'Home/health_campaigns.html', context)

def our_partners(request):
    """Liste des partenaires par type"""
    settings = SiteSettings.get_settings()
    partners = Partner.objects.filter(is_active=True)
    
    # Grouper par type
    partners_by_type = {}
    for partner in partners:
        type_display = partner.get_partner_type_display()
        if type_display not in partners_by_type:
            partners_by_type[type_display] = []
        partners_by_type[type_display].append(partner)
    
    context = {
        'settings': settings,
        'partners_by_type': partners_by_type,
    }
    return render(request, 'Home/partners.html', context)

def testimonials_list(request):
    """Liste des témoignages"""
    settings = SiteSettings.get_settings()
    testimonials = Testimonial.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'testimonials': testimonials,
    }
    return render(request, 'Home/testimonials.html', context)

@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def contact_us(request):
    """Page de contact avec formulaire"""
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            # Capturer l'adresse IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                message.ip_address = x_forwarded_for.split(',')[0]
            else:
                message.ip_address = request.META.get('REMOTE_ADDR')
            message.save()
            
            messages.success(
                request, 
                'Votre message a été envoyé avec succès. '
                'Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('contact_us')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = ContactMessageForm()
    
    context = {
        'settings': settings,
        'form': form,
    }
    return render(request, 'Home/contact.html', context)


# ========================================
# DETAIL PAGES
# ========================================
def service_detail(request, service_slug):
    """Détail d'un service"""
    settings = SiteSettings.get_settings()
    service = get_object_or_404(Service, slug=service_slug, is_active=True)
    staff_members = service.staff_members.filter(is_visible=True)
    
    context = {
        'settings': settings,
        'service': service,
        'staff_members': staff_members,
    }
    return render(request, 'services/service_detail.html', context)

def doctor_detail(request, doctor_id):
    """Fiche détaillée d'un membre du personnel"""
    settings = SiteSettings.get_settings()
    staff = get_object_or_404(Staff, id=doctor_id, is_visible=True)
    
    context = {
        'settings': settings,
        'staff': staff,
    }
    return render(request, 'doctors/doctor_detail.html', context)

def news_detail(request, news_id):
    """Détail d'un article"""
    settings = SiteSettings.get_settings()
    article = get_object_or_404(Article, id=news_id, status='published')
    
    # Incrémenter les vues
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    # Articles similaires
    similar_articles = Article.objects.filter(
        category=article.category, 
        status='published'
    ).exclude(id=article.id)[:3]
    
    context = {
        'settings': settings,
        'article': article,
        'similar_articles': similar_articles,
    }
    return render(request, 'news/news_detail.html', context)

@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def campaign_detail(request, campaign_id):
    """Détail d'une campagne avec formulaire d'inscription"""
    settings = SiteSettings.get_settings()
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    if request.method == 'POST' and campaign.registration_enabled:
        form = CampaignRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.campaign = campaign
            registration.save()
            messages.success(request, 'Inscription confirmée ! Nous vous contacterons bientôt.')
            return redirect('campaign_detail', campaign_id=campaign.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CampaignRegistrationForm()
    
    context = {
        'settings': settings,
        'campaign': campaign,
        'form': form,
    }
    return render(request, 'campaigns/campaign_detail.html', context)


# ========================================
# RENDEZ-VOUS
# ========================================
@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def appointment_create(request):
    """Formulaire de prise de rendez-vous"""
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            
            messages.success(
                request, 
                'Votre demande de rendez-vous a été envoyée avec succès. '
                'Nous vous contacterons bientôt pour confirmation.'
            )
            return redirect('appointment_success')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = AppointmentForm()
    
    context = {
        'settings': settings,
        'form': form,
    }
    return render(request, 'Home/appointment_form.html', context)

def appointment_success(request):
    """Page de confirmation après rendez-vous"""
    settings = SiteSettings.get_settings()
    return render(request, 'Home/appointment_success.html', {'settings': settings})


# ========================================
# API AJAX
# ========================================
def get_staff_by_service(request):
    """API pour récupérer les médecins d'un service (AJAX)"""
    service_id = request.GET.get('service_id')
    
    if not service_id:
        return JsonResponse({'staff': []})
    
    staff_members = Staff.objects.filter(
        services__id=service_id,
        accepts_appointments=True,
        is_visible=True
    ).values('id', 'first_name', 'last_name', 'grade', 'speciality')
    
    staff_list = []
    for staff in staff_members:
        grade_display = dict(Staff.GRADE_CHOICES).get(staff['grade'], staff['grade'])
        staff_list.append({
            'id': staff['id'],
            'name': f"{grade_display} {staff['first_name']} {staff['last_name']}",
            'speciality': staff['speciality']
        })
    
    return JsonResponse({'staff': staff_list})