from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteSettings, Page, Service, Staff, Category, Article, ArticleImage,
    Campaign, CampaignImage, CampaignRegistration, Partner, Appointment, 
    ContactMessage, Testimonial, DirectionMember
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
            'fields': ('organization_chart', 'certifications')
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
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
    list_display = ('full_name', 'grade', 'speciality', 'is_chief', 'is_visible', 'accepts_appointments')
    list_filter = ('grade', 'is_chief', 'is_visible', 'accepts_appointments', 'services')
    search_fields = ('first_name', 'last_name', 'speciality')
    filter_horizontal = ('services',)
    list_editable = ('accepts_appointments', 'is_visible')
    
    fieldsets = (
        ('Identité', {
            'fields': ('first_name', 'last_name', 'photo')
        }),
        ('Informations personnelles', {
            'fields': ('grade', 'speciality', 'is_chief')
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
# CATÉGORIES
# ========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count')
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.article_set.count()
    article_count.short_description = 'Articles'


# ========================================
# IMAGES D'ARTICLES (Inline)
# ========================================
class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('image', 'caption', 'display_order')


# ========================================
# ACTUALITÉS
# ========================================
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    list_editable = ('status',)
    inlines = [ArticleImageInline]
    
    fieldsets = (
        ('Contenu principal', {
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
# IMAGES DE CAMPAGNES (Inline)
# ========================================
class CampaignImageInline(admin.TabularInline):
    model = CampaignImage
    extra = 1
    fields = ('image', 'caption', 'display_order')


# ========================================
# INSCRIPTIONS AUX CAMPAGNES (Inline)
# ========================================
class CampaignRegistrationInline(admin.TabularInline):
    model = CampaignRegistration
    extra = 0
    readonly_fields = ('full_name', 'email', 'phone', 'age', 'reason', 'registered_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# ========================================
# CAMPAGNES DE SANTÉ
# ========================================
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location', 'status', 
                   'registration_enabled', 'registrations_count')
    list_filter = ('status', 'start_date', 'registration_enabled')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    list_editable = ('status', 'registration_enabled')
    inlines = [CampaignImageInline, CampaignRegistrationInline]
    
    fieldsets = (
        ('Contenu principal', {
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
    
    def registrations_count(self, obj):
        return obj.registrations.count()
    registrations_count.short_description = 'Inscriptions'


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
    
    @admin.action(description="Marquer comme Confirmé")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    
    @admin.action(description="Marquer comme Honoré")
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    
    @admin.action(description="Marquer comme Annulé")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')


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
    
    @admin.action(description="Marquer comme Lu")
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    
    @admin.action(description="Marquer comme Répondu")
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')


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


# ========================================
# INSCRIPTIONS AUX CAMPAGNES (Vue séparée)
# ========================================
@admin.register(CampaignRegistration)
class CampaignRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'campaign', 'email', 'phone', 'registered_at')
    list_filter = ('campaign', 'registered_at')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('registered_at',)
    date_hierarchy = 'registered_at'


# Personnalisation de l'admin
admin.site.site_header = "Administration HRAE"
admin.site.site_title = "HRAE Admin"
admin.site.index_title = "Gestion du site web"