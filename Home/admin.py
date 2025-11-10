from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ArticleImage, SiteSettings, Page, Service, Staff, Category, Article,
    Campaign, Partner, Appointment, ContactMessage, Testimonial, DirectionMember
)


# ========================================
# PARAMÈTRES DU SITE
# ========================================
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'site_tagline', 'logo')
        }),
        ('Contact', {
            'fields': ('phone', 'emergency_phone', 'email', 'address')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Chiffres clés', {
            'fields': ('patients_per_year', 'beds_count', 'specialties_count', 'staff_count', 'success_rate')
        }),
        ('À propos', {
            'fields': ('organization_chart',)
        }),
    )
    
    def has_add_permission(self, request):
        # Ne permettre qu'une seule instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False


# ========================================
# PAGES STATIQUES
# ========================================
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
    )


# ========================================
# SERVICES MÉDICAUX
# ========================================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_active', 'staff_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'is_active')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'icon', 'short_description', 'banner_image')
        }),
        ('Description complète', {
            'fields': ('full_description',)
        }),
        ('Détails médicaux', {
            'fields': ('pathologies', 'equipment', 'admission_conditions'),
            'classes': ('collapse',)
        }),
        ('Informations pratiques', {
            'fields': ('consultation_hours', 'tariffs', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('display_order', 'is_active')
        }),
    )
    
    def staff_count(self, obj):
        return obj.staff_members.count()
    staff_count.short_description = 'Personnel'


# ========================================
# PERSONNEL MÉDICAL
# ========================================
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('photo_thumbnail', 'full_name', 'grade', 'speciality', 
                   'accepts_appointments', 'is_visible')
    list_filter = ('grade', 'accepts_appointments', 'is_visible', 'services')
    search_fields = ('first_name', 'last_name', 'speciality')
    filter_horizontal = ('services',)
    list_editable = ('accepts_appointments', 'is_visible')
    
    fieldsets = (
        ('Identité', {
            'fields': ('first_name', 'last_name', 'photo', 'grade')
        }),
        ('Informations professionnelles', {
            'fields': ('speciality', 'services', 'diplomas', 'experience', 'expertise', 'languages')
        }),
        ('Rendez-vous', {
            'fields': ('accepts_appointments', 'consultation_duration', 'consultation_hours'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('email', 'phone'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('is_visible', 'display_order')
        }),
    )
    
    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', 
                             obj.photo.url)
        return '-'
    photo_thumbnail.short_description = 'Photo'


# ========================================
# ACTUALITÉS
# ========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count')
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.article_set.count()
    article_count.short_description = 'Articles'

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('image', 'caption', 'display_order')
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    list_editable = ('status',)
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Classification', {
            'fields': ('category', 'author', 'status', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


# ========================================
# CAMPAGNES DE SANTÉ
# ========================================
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location', 'status', 'registration_enabled')
    list_filter = ('status', 'start_date')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    list_editable = ('status', 'registration_enabled')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'slug', 'banner_image', 'short_description')
        }),
        ('Description complète', {
            'fields': ('full_description', 'objectives')
        }),
        ('Dates et lieu', {
            'fields': ('start_date', 'end_date', 'location', 'schedule')
        }),
        ('Détails', {
            'fields': ('services_offered', 'target_audience'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('contact_name', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('registration_enabled', 'status')
        }),
    )


# ========================================
# PARTENAIRES
# ========================================
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('logo_thumbnail', 'name', 'partner_type', 'is_active', 'display_order')
    list_filter = ('partner_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'display_order')
    
    fieldsets = (
        ('Informations', {
            'fields': ('name', 'logo', 'partner_type', 'description', 'website')
        }),
        ('Collaboration', {
            'fields': ('collaboration_domain',),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('display_order', 'is_active')
        }),
    )
    
    def logo_thumbnail(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return '-'
    logo_thumbnail.short_description = 'Logo'


# ========================================
# RENDEZ-VOUS
# ========================================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'service', 'staff', 'appointment_date', 
                   'status', 'created_at')
    list_filter = ('status', 'service', 'staff', 'appointment_date')
    search_fields = ('patient_name', 'patient_email', 'patient_phone')
    date_hierarchy = 'appointment_date'
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient_name', 'patient_email', 'patient_phone', 'patient_birthdate')
        }),
        ('Rendez-vous', {
            'fields': ('service', 'staff', 'appointment_date', 'duration', 'status')
        }),
        ('Détails', {
            'fields': ('reason', 'is_first_visit', 'insurance_number'),
            'classes': ('collapse',)
        }),
        ('Gestion interne', {
            'fields': ('internal_notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Marquer comme Confirmé"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Marquer comme Honoré"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Marquer comme Annulé"


# ========================================
# MESSAGES DE CONTACT
# ========================================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'ip_address')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    
    fieldsets = (
        ('Expéditeur', {
            'fields': ('name', 'email', 'phone', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Gestion', {
            'fields': ('status', 'ip_address', 'created_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = "Marquer comme Lu"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = "Marquer comme Répondu"


# ========================================
# TÉMOIGNAGES
# ========================================
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'service', 'rating', 'is_active', 'display_order')
    list_filter = ('is_active', 'service', 'rating')
    search_fields = ('patient_name', 'testimonial')
    list_editable = ('is_active', 'display_order')
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient_name', 'patient_photo', 'service')
        }),
        ('Témoignage', {
            'fields': ('testimonial', 'rating')
        }),
        ('Gestion', {
            'fields': ('is_active', 'display_order')
        }),
    )


# ========================================
# ÉQUIPE DE DIRECTION
# ========================================
@admin.register(DirectionMember)
class DirectionMemberAdmin(admin.ModelAdmin):
    list_display = ('photo_thumbnail', 'full_name', 'position', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('first_name', 'last_name', 'position')
    list_editable = ('is_active', 'display_order')
    
    fieldsets = (
        ('Identité', {
            'fields': ('first_name', 'last_name', 'photo', 'position')
        }),
        ('Biographie', {
            'fields': ('bio',)
        }),
        ('Contact', {
            'fields': ('email', 'phone'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('display_order', 'is_active')
        }),
    )
    
    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', 
                             obj.photo.url)
        return '-'
    photo_thumbnail.short_description = 'Photo'


# Personnalisation de l'admin
admin.site.site_header = "Administration HRAE"
admin.site.site_title = "HRAE Admin"
admin.site.index_title = "Gestion du site web"