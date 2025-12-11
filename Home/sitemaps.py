"""
Sitemaps pour l'indexation Google du site HRAE
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Service, Staff, Article, Campaign, Page


class StaticViewSitemap(Sitemap):
    """Pages statiques du site"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'about',
            'services',
            'team',
            'news',
            'health_campaigns',
            'our_partners',
            'testimonials',
            'practical_info',
            'contact_us',
            'appointment',
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """Services médicaux"""
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Service.objects.filter(is_active=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('service_detail', args=[obj.slug])


class ArticleSitemap(Sitemap):
    """Articles d'actualité"""
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('news_detail', args=[obj.id])


class CampaignSitemap(Sitemap):
    """Campagnes de santé"""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Campaign.objects.all().order_by('-start_date')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('campaign_detail', args=[obj.id])


class StaffSitemap(Sitemap):
    """Personnel médical"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Staff.objects.filter(is_visible=True).order_by('last_name')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('doctor_detail', args=[obj.id])


class PageSitemap(Sitemap):
    """Pages statiques personnalisées"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Page.objects.filter(is_active=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/page/{obj.slug}/'
