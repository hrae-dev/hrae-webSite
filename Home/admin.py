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
            'fields': ('site_name', 'site_tagline', 'logo', 'favicon'),
            'description': 'Informations de base affichées sur tout le site'
        }),
        ('Contact', {
            'fields': ('address', 'phone', 'emergency_phone', 'email'),
            'description': 'Coordonnées affichées dans le footer et la page contact'
        }),
        ('Horaires', {
            'fields': ('opening_hours', 'emergency_hours'),
            'description': 'Horaires d\'ouverture et disponibilité des urgences'
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url'),
            'description': 'Liens vers vos pages de réseaux sociaux (laisser vide pour masquer l\'icône)',
            'classes': ('collapse',)
        }),
        ('📖 Notre Histoire', {
            'fields': ('history',),
            'description': '''
                <strong>Section "Notre Histoire" de la page À propos</strong><br>
                Racontez l'évolution de l'hôpital, ses moments clés, ses réalisations.<br><br>
                <strong>💡 Conseils de rédaction :</strong><br>
                • Parlez de la fondation de l'hôpital (quand, pourquoi, par qui)<br>
                • Mentionnez les étapes importantes (agrandissements, nouveaux services)<br>
                • Évoquez les réalisations et impacts sur la communauté<br>
                • Gardez un ton positif et inspirant<br><br>
                <strong>🎨 Mise en forme (HTML autorisé) :</strong><br>
                • &lt;p&gt;...&lt;/p&gt; pour les paragraphes<br>
                • &lt;strong&gt;...&lt;/strong&gt; pour le texte en gras<br>
                • &lt;em&gt;...&lt;/em&gt; pour l'italique<br>
                • &lt;br&gt; pour sauter une ligne<br>
                • &lt;ul&gt;&lt;li&gt;...&lt;/li&gt;&lt;/ul&gt; pour les listes à puces
            '''
        }),
        ('🎯 Mission', {
            'fields': ('mission',),
            'description': '''
                <strong>Notre Mission</strong> - Quelle est la raison d'être de l'hôpital ?<br><br>
                <em>Exemple :</em><br>
                "Fournir des soins de santé de qualité, accessibles et centrés sur le patient, 
                tout en contribuant au développement de la santé publique dans la région de la Sanaga-Maritime."<br><br>
                <strong>Longueur recommandée :</strong> 2-4 phrases
            '''
        }),
        ('🔭 Vision', {
            'fields': ('vision',),
            'description': '''
                <strong>Notre Vision</strong> - Où voulez-vous être dans le futur ?<br><br>
                <em>Exemple :</em><br>
                "Devenir le centre de référence en matière de soins de santé dans la région, 
                reconnu pour son excellence médicale, ses infrastructures modernes et son engagement 
                envers la communauté."<br><br>
                <strong>Longueur recommandée :</strong> 2-4 phrases
            '''
        }),
        ('💎 Valeurs', {
            'fields': ('values',),
            'description': '''
                <strong>Nos Valeurs</strong> - Les principes qui guident vos actions quotidiennes.<br><br>
                <em>Exemple :</em><br>
                "Excellence médicale<br>
                Compassion et empathie<br>
                Intégrité et transparence<br>
                Innovation et amélioration continue<br>
                Respect de la dignité humaine"<br><br>
                <strong>💡 Conseil :</strong> Listez 4-6 valeurs, une par ligne
            '''
        }),
        ('📊 Chiffres clés', {
            'fields': ('patients_per_year', 'beds_count', 'specialties_count', 
                      'staff_count', 'years_of_experience', 'success_rate'),
            'description': '''
                <strong>Statistiques affichées sur la page À propos</strong><br>
                Ces chiffres illustrent l'impact et l'envergure de l'hôpital.<br><br>
                • <strong>Patients par an :</strong> Nombre de patients reçus annuellement<br>
                • <strong>Nombre de lits :</strong> Capacité d'hospitalisation<br>
                • <strong>Spécialités :</strong> Nombre de services médicaux<br>
                • <strong>Personnel :</strong> Nombre total d'employés<br>
                • <strong>Années d'expérience :</strong> Depuis la fondation<br>
                • <strong>Taux de succès :</strong> Pourcentage (ex: 95.50 pour 95,5%)
            ''',
            'classes': ('collapse',)
        }),
        ('📄 Documents', {
            'fields': ('organization_chart', 'certifications'),
            'description': '''
                <strong>📋 Organigramme :</strong> Image de la structure organisationnelle de l'hôpital<br>
                <em>Format recommandé : PNG ou JPG, largeur minimale 1200px</em><br><br>
                
                <strong>🏆 Certifications :</strong> Liste des certifications et accréditations<br>
                <em>Une certification par ligne, exemple :</em><br>
                ISO 9001:2015<br>
                Accréditation Ministère de la Santé Publique<br>
                Certification HAS (Haute Autorité de Santé)<br>
                Membre du Réseau Hospitalier Africain
            ''',
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Un seul objet SiteSettings autorisé
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Interdire la suppression des paramètres
        return False
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, "✅ Les paramètres du site ont été mis à jour avec succès!", level='success')
        else:
            self.message_user(request, "✅ Les paramètres du site ont été créés avec succès!", level='success')


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
    list_display = ('name', 'display_order', 'is_active', 'show_on_homepage', 'staff_count')
    list_filter = ('is_active', 'show_on_homepage')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'is_active', 'show_on_homepage')
    
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
            'fields': ('display_order', 'is_active', 'show_on_homepage'),
            'description': '<p style="color: #666;">Cochez "Afficher sur la page d\'accueil" pour que ce service apparaisse sur la page d\'accueil (maximum 6 services)</p>'
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
        ('Informations professionnelles', {
            'fields': ('grade', 'speciality', 'services', 'is_chief')
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