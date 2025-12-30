from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    SiteSettings, PatientJourneySection, PatientJourneyStep,
    Page, Service, ServiceImage, Staff, Category, Article, ArticleImage,
    Campaign, CampaignImage, CampaignRegistration, Partner, Appointment,
    ContactMessage, Testimonial, DirectionMember,
    AboutPage, Award, TimelineItem, HospitalSpecialty, RecentEquipment, FormerDirector
)


# ========================================
# PARAMÈTRES DU SITE
# ========================================
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'site_tagline', 'logo', 'favicon'),
        }),
        ('Contact', {
            'fields': ('address', 'phone', 'emergency_phone', 'email'),
        }),
        ('Horaires', {
            'fields': (
                ('weekday_label', 'weekday_hours'),
                ('saturday_label', 'saturday_hours'),
                ('on_call_label', 'on_call_hours'),
                ('emergency_label', 'emergency_hours_display'),
                'opening_hours',
                'emergency_hours',
            ),
            'description': 'Les horaires affichés dans le footer du site',
        }),
        ('Tarifs & Paiements', {
            'fields': ('payment_modes', 'accepted_insurances'),
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Notre Histoire', {
            'fields': ('history',),
        }),
        ('Mission', {
            'fields': ('mission',),
        }),
        ('Vision', {
            'fields': ('vision',),
        }),
        ('Valeurs', {
            'fields': ('values',),
        }),
        ('Chiffres clés', {
            'fields': ('patients_per_year', 'beds_count', 'specialties_count',
                    'staff_count', 'years_of_experience', 'success_rate'),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('organization_chart', 'certifications'),
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
            self.message_user(request, "Les paramètres du site ont été mis à jour avec succès!", level='success')
        else:
            self.message_user(request, "Les paramètres du site ont été créés avec succès!", level='success')


# ========================================
# PARCOURS PATIENT
# ========================================
class PatientJourneyStepInline(admin.TabularInline):
    """Étapes d'une section du parcours patient (affichage en ligne)"""
    model = PatientJourneyStep
    extra = 1
    fields = ('title', 'description', 'display_order')
    verbose_name = "Étape"
    verbose_name_plural = "Étapes du parcours"


@admin.register(PatientJourneySection)
class PatientJourneySectionAdmin(admin.ModelAdmin):
    """Administration des sections du parcours patient"""
    list_display = ('name', 'display_order', 'is_active', 'steps_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('display_order', 'is_active')
    inlines = [PatientJourneyStepInline]

    fieldsets = (
        ('Informations de la section', {
            'fields': ('name', 'display_order', 'is_active'),
        }),
    )

    def steps_count(self, obj):
        count = obj.steps.count()
        return format_html(
            '<span style="background: #e7f3ff; padding: 3px 10px; border-radius: 10px; color: #0066cc;">{} étape{}</span>',
            count,
            's' if count > 1 else ''
        )
    steps_count.short_description = 'Nombre d\'étapes'


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
# IMAGES DE SERVICES (Inline)
# ========================================
class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'caption', 'display_order')


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
    inlines = [ServiceImageInline]

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
    list_display = ('photo_thumbnail', 'title', 'full_name_display', 'grade', 'quality', 'speciality', 'is_visible')
    list_filter = ('title', 'grade', 'quality', 'is_visible', 'accepts_appointments', 'services')
    search_fields = ('first_name', 'last_name', 'speciality')
    filter_horizontal = ('services',)
    list_editable = ('is_visible',)

    class Media:
        js = ('admin/js/staff_admin.js',)
        css = {
            'all': ('admin/css/staff_admin.css',)
        }

    fieldsets = (
        ('📋 Informations de base', {
            'fields': (
                'title',
                ('first_name', 'last_name'),
                'photo',
                ('grade', 'speciality'),
            ),
            'description': mark_safe('Entrez les informations essentielles du membre du personnel.')
        }),
        ('🏥 Affectation et Fonction', {
            'fields': (
                'quality',
                'services',
            ),
            'description': mark_safe(
                '<strong style="color: #0066cc;">💡 Conseil :</strong><br>'
                '• <strong>Qualité :</strong> Choisissez "Chef de service" pour afficher cette personne dans le carousel en haut de la page "Notre Équipe". Choisissez "Major" ou laissez vide si aucune fonction spéciale.<br>'
                '• <strong>Services :</strong> Optionnel. Pour les directeurs, vous pouvez le laisser vide ou sélectionner "Direction".'
            )
        }),
        ('📞 Contact', {
            'fields': ('email', 'phone'),
            'classes': ('collapse',)
        }),
        ('📅 Rendez-vous en ligne', {
            'fields': ('accepts_appointments', 'consultation_duration', 'consultation_hours'),
            'classes': ('collapse',),
            'description': mark_safe('Activez cette option si le membre peut recevoir des demandes de rendez-vous en ligne.')
        }),
        ('📝 Informations détaillées (optionnel)', {
            'fields': ('diplomas', 'experience', 'expertise', 'languages'),
            'classes': ('collapse',),
            'description': mark_safe('Ces informations enrichissent le profil mais ne sont pas obligatoires.')
        }),
        ('⚙️ Paramètres d\'affichage', {
            'fields': ('is_visible', 'display_order'),
            'description': mark_safe('✓ Cochez <strong>"Affiché sur le site"</strong> pour que cette personne apparaisse sur le site web.')
        }),
    )

    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                             obj.photo.url)
        return '-'
    photo_thumbnail.short_description = 'Photo'

    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name_display.short_description = 'Nom complet'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Personnaliser les labels des champs ManyToMany"""
        if db_field.name == "services":
            kwargs['help_text'] = 'Optionnel : sélectionnez un ou plusieurs services. Pour les directeurs, laissez vide ou choisissez "Direction".'
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            self.message_user(request, f"✓ {obj.full_name} ajouté avec succès!", level='success')
        else:
            self.message_user(request, f"✓ {obj.full_name} mis à jour avec succès!", level='success')


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


# ========================================
# PAGE "À PROPOS"
# ========================================

# Inlines pour la page À propos
class AwardInline(admin.TabularInline):
    model = Award
    extra = 1
    fields = ('title', 'image', 'badge', 'display_order', 'is_active')
    readonly_fields = ()
    verbose_name = "Distinction"
    verbose_name_plural = "Distinctions"


class TimelineItemInline(admin.StackedInline):
    model = TimelineItem
    extra = 1
    fields = ('title', 'description', 'icon', 'image', 'display_order', 'is_active')
    verbose_name = "Élément de l'histoire"
    verbose_name_plural = "Timeline - Notre Histoire"


class HospitalSpecialtyInline(admin.StackedInline):
    model = HospitalSpecialty
    extra = 1
    fields = ('title', 'description', 'image', 'display_order', 'is_active')
    verbose_name = "Spécialité"
    verbose_name_plural = "Spécialités de l'hôpital"


class RecentEquipmentInline(admin.StackedInline):
    model = RecentEquipment
    extra = 1
    fields = ('title', 'description', 'image', 'display_order', 'is_active')
    verbose_name = "Équipement récent"
    verbose_name_plural = "Équipements récents"


class FormerDirectorInline(admin.StackedInline):
    model = FormerDirector
    extra = 1
    fields = ('title_prefix', 'first_name', 'last_name', 'photo', 'period', 'description', 'display_order', 'is_active')
    verbose_name = "Ancien directeur"
    verbose_name_plural = "Anciens directeurs"


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    readonly_fields = ('director_photo_preview',)
    inlines = [AwardInline, TimelineItemInline, HospitalSpecialtyInline, RecentEquipmentInline, FormerDirectorInline]

    fieldsets = (
        ('Mot du Directeur', {
            'fields': ('director_message_title', 'director_message', 'director_photo', 'director_photo_preview', 'director_name'),
        }),
        ('Section Humanisme', {
            'fields': (
                'humanism_title',
                'humanism_intro',
                ('humanism_point1_title', 'humanism_point1_text'),
                ('humanism_point2_title', 'humanism_point2_text'),
                ('humanism_point3_title', 'humanism_point3_text'),
            ),
        }),
        ('Section Qualité', {
            'fields': (
                'quality_title',
                'quality_intro',
                ('quality_point1_title', 'quality_point1_text'),
                ('quality_point2_title', 'quality_point2_text'),
                ('quality_point3_title', 'quality_point3_text'),
            ),
        }),
        ('Section Avenir', {
            'fields': ('future_title', 'future_text', 'future_quote'),
        }),
        ('Section Importance stratégique', {
            'fields': (
                'strategic_title',
                'strategic_intro',
                ('strategic_point1_title', 'strategic_point1_text'),
                ('strategic_point2_title', 'strategic_point2_text'),
                ('strategic_point3_title', 'strategic_point3_text'),
                'google_maps_embed_url',
            ),
        }),
        ('Titres des sections', {
            'fields': (
                'specialties_section_title',
                'equipment_section_title',
                'equipment_intro',
                'directors_section_title',
                'directors_intro',
            ),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def director_photo_preview(self, obj):
        if obj.director_photo:
            return format_html('<img src="{}" width="150" style="border-radius: 8px;" />', obj.director_photo.url)
        return "Aucune photo"
    director_photo_preview.short_description = 'Aperçu photo directeur'


# Note: Les modèles Award, TimelineItem, HospitalSpecialty, RecentEquipment et FormerDirector
# sont gérés via des inlines dans AboutPageAdmin ci-dessus.
# Ils n'apparaissent plus comme des menus séparés dans l'admin.


# Personnalisation de l'admin
admin.site.site_header = "Administration HRAE"
admin.site.site_title = "HRAE Admin"
admin.site.index_title = "Gestion du site web"