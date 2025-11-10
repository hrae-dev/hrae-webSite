from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    SiteSettings, Page, Service, Staff, Article, Category,
    Campaign, Partner, Appointment, ContactMessage, Testimonial, DirectionMember
)
from .forms import AppointmentForm, CampaignRegistrationForm, ContactMessageForm
from django.utils import timezone


# ========================================
# MAIN PAGES
# ========================================
def index(request):
    """Page d'accueil avec tous les éléments"""
    settings = SiteSettings.get_settings()
    services = Service.objects.filter(is_active=True)[:4]
    articles = Article.objects.filter(status='published').order_by('-published_at')[:3]
    testimonials = Testimonial.objects.filter(is_active=True)[:3]
    partners = Partner.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'services': services,
        'articles': articles,
        'testimonials': testimonials,
        'partners': partners,
    }
    return render(request, 'Home/index.html', context)


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
    """Liste des services"""
    settings = SiteSettings.get_settings()
    services = Service.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'services': services,
    }
    return render(request, 'Home/services.html', context)


def our_team(request):
    """Liste de l'équipe médicale avec filtres"""
    settings = SiteSettings.get_settings()
    staff_list = Staff.objects.filter(is_visible=True)
    
    # Filtres
    service_id = request.GET.get('service')
    grade = request.GET.get('grade')
    search = request.GET.get('search')
    
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
    
    services = Service.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'staff_list': staff_list,
        'services': services,
        'grades': Staff.GRADE_CHOICES,
    }
    return render(request, 'Home/our_team.html', context)


def news(request):
    """Liste des actualités avec pagination"""
    settings = SiteSettings.get_settings()
    articles_list = Article.objects.filter(status='published')
    
    # Filtres
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    if category_id:
        articles_list = articles_list.filter(category_id=category_id)
    if search:
        articles_list = articles_list.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(articles_list, 9)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'settings': settings,
        'articles': articles,
        'categories': categories,
    }
    return render(request, 'Home/news.html', context)



def health_campaigns(request):
    """Liste des campagnes groupées par statut"""
    settings = SiteSettings.get_settings()
    today = timezone.now().date()
    
    # Calculer automatiquement le statut basé sur les dates
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
    """Liste des partenaires"""
    settings = SiteSettings.get_settings()
    partners = Partner.objects.filter(is_active=True)
    
    # Grouper par type
    partners_by_type = {}
    for partner_type, label in Partner.TYPE_CHOICES:
        partners_by_type[label] = partners.filter(partner_type=partner_type)
    
    context = {
        'settings': settings,
        'partners': partners,
        'partners_by_type': partners_by_type,
    }
    return render(request, 'Home/our_partners.html', context)


def practical_info(request):
    """Informations pratiques"""
    settings = SiteSettings.get_settings()
    page = Page.objects.filter(slug='informations-pratiques', is_active=True).first()
    
    context = {
        'settings': settings,
        'page': page,
    }
    return render(request, 'Home/practical_info.html', context)


def contact_us(request):
    """Page de contact avec formulaire"""
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            # Capturer l'IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                message.ip_address = x_forwarded_for.split(',')[0]
            else:
                message.ip_address = request.META.get('REMOTE_ADDR')
            
            message.save()
            
            messages.success(
                request, 
                'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
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
def service_detail(request, service_id):
    """Détail d'un service"""
    settings = SiteSettings.get_settings()
    service = get_object_or_404(Service, id=service_id, is_active=True)
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


def campaign_detail(request, campaign_id):
    settings = SiteSettings.get_settings()
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    if request.method == 'POST' and campaign.registration_enabled:
        form = CampaignRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.campaign = campaign
            registration.save()
            messages.success(request, 'Inscription confirmée !')
            return redirect('campaign_detail', campaign_id=campaign.id)
    else:
        form = CampaignRegistrationForm()
    
    return render(request, 'campaigns/campaign_detail.html', {
        'settings': settings,
        'campaign': campaign,
        'form': form,
    })

# ========================================
# RENDEZ-VOUS
# ========================================
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