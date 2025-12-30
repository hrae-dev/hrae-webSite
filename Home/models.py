from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.db.models import JSONField
from django_ckeditor_5.fields import CKEditor5Field

# ========================================
# PARAMÈTRES GÉNÉRAUX DU SITE
# ========================================
class SiteSettings(models.Model):
    """Paramètres généraux du site (unique instance)"""
    # Informations générales
    site_name = models.CharField("Nom de l'hôpital", max_length=255, default="HRAE")
    site_tagline = models.CharField("Slogan", max_length=255, blank=True)
    logo = models.ImageField("Logo", upload_to='settings/', blank=True)
    favicon = models.ImageField("Favicon", upload_to='settings/', blank=True)
    
    # Contact
    phone = models.CharField("Téléphone standard", max_length=20)
    emergency_phone = models.CharField("Urgences 24/7", max_length=20)
    email = models.EmailField("Email général")
    address = models.TextField("Adresse complète")
    
    # Horaires
    opening_hours = models.CharField(
        "Horaires d'ouverture",
        max_length=200,
        default="Lun-Dim 8h-15h30",
        help_text="Horaires de consultation"
    )
    emergency_hours = models.CharField(
        "Horaires urgences",
        max_length=200,
        default="24h/24, 7j/7"
    )

    # Horaires détaillés pour le footer
    weekday_label = models.CharField(
        "Libellé jours semaine",
        max_length=50,
        default="Lun - Ven",
        help_text="Ex: Lun - Ven, Du lundi au vendredi"
    )
    weekday_hours = models.CharField(
        "Horaires semaine",
        max_length=100,
        default="8h - 17h",
        help_text="Horaires du lundi au vendredi"
    )
    saturday_label = models.CharField(
        "Libellé samedi",
        max_length=50,
        default="Samedi",
        help_text="Ex: Samedi, Sam."
    )
    saturday_hours = models.CharField(
        "Horaires samedi",
        max_length=100,
        default="8h - 13h",
        help_text="Horaires du samedi"
    )
    emergency_label = models.CharField(
        "Libellé urgences",
        max_length=50,
        default="Urgences",
        help_text="Ex: Urgences, Service d'urgence"
    )
    emergency_hours_display = models.CharField(
        "Disponibilité urgences",
        max_length=100,
        default="24/7",
        help_text="Ex: 24/7, 24h/24 7j/7"
    )
    on_call_label = models.CharField(
        "Libellé garde",
        max_length=50,
        default="Garde",
        help_text="Ex: Garde, Permanence"
    )
    on_call_hours = models.CharField(
        "Horaires de garde",
        max_length=100,
        default="17h - 8h",
        help_text="Horaires de la garde"
    )

    # Tarifs & Paiements
    payment_modes = models.TextField(
        "Modes de paiement acceptés",
        blank=True,
        help_text="Un mode par ligne. Ex: Espèces, Mobile Money (OM, Momo), Carte bancaire"
    )
    accepted_insurances = models.TextField(
        "Mutuelles acceptées",
        blank=True,
        help_text="Une mutuelle par ligne"
    )
 


    
    # Réseaux sociaux
    facebook_url = models.URLField("Facebook", blank=True)
    twitter_url = models.URLField("Twitter", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)
    
    # Contenus éditoriaux
    history = CKEditor5Field("Notre Histoire", blank=True,
                               help_text="Histoire de l'hôpital affichée sur la page À propos")
    mission = CKEditor5Field("Notre mission", blank=True)
    vision = CKEditor5Field("Notre vision", blank=True)
    values = CKEditor5Field("Nos valeurs", blank=True,
                              help_text="Une valeur par ligne")
    
    # Chiffres clés
    patients_per_year = models.IntegerField("Patients par an", default=0)
    beds_count = models.IntegerField("Nombre de lits", default=0)
    specialties_count = models.IntegerField("Nombre de spécialités", default=0)
    staff_count = models.IntegerField("Nombre de personnel", default=0)
    years_of_experience = models.IntegerField("Années d'expérience", default=0)
    success_rate = models.DecimalField("Taux de succès (%)", max_digits=5, 
                                      decimal_places=2, default=0, blank=True)
    
    # Documents
    organization_chart = models.ImageField("Organigramme administratif", 
                                          upload_to='settings/', blank=True)
    certifications = models.TextField("Certifications et accréditations", blank=True,
                                     help_text="Une par ligne")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# ========================================
# PARCOURS PATIENT
# ========================================
class PatientJourneySection(models.Model):
    """Sections du parcours patient (Urgence, Consultation, Documents...)"""
    name = models.CharField("Nom de la section", max_length=255,
                           help_text="Ex: Situation d'urgence, Consultation / Visite, Documents à prévoir")
    display_order = models.IntegerField("Ordre d'affichage", default=0,
                                       help_text="Plus petit = affiché en premier")
    is_active = models.BooleanField("Actif", default=True)

    class Meta:
        verbose_name = "Section du parcours patient"
        verbose_name_plural = "Sections du parcours patient"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class PatientJourneyStep(models.Model):
    """Étapes d'une section du parcours patient"""
    section = models.ForeignKey(PatientJourneySection, on_delete=models.CASCADE,
                               related_name='steps', verbose_name="Section")
    title = models.CharField("Titre de l'étape", max_length=255,
                            help_text="Ex: Brancardier, Infirmier(ère), Carnet de santé")
    description = models.TextField("Description",
                                   help_text="Explication de cette étape")
    display_order = models.IntegerField("Ordre d'affichage", default=0,
                                       help_text="Plus petit = affiché en premier")

    class Meta:
        verbose_name = "Étape du parcours patient"
        verbose_name_plural = "Étapes du parcours patient"
        ordering = ['section', 'display_order', 'title']

    def __str__(self):
        return f"{self.section.name} - {self.title}"


# ========================================
# PAGES STATIQUES
# ========================================
class Page(models.Model):
    """Pages statiques (À propos, Infos pratiques, etc.)"""
    title = models.CharField("Titre", max_length=255)
    slug = models.SlugField("URL", unique=True)
    content = CKEditor5Field("Contenu")
    meta_description = models.CharField("Description SEO", max_length=160, blank=True)
    is_active = models.BooleanField("Actif", default=True)
    updated_at = models.DateTimeField("Dernière modification", auto_now=True)
    
    class Meta:
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ========================================
# SERVICES MÉDICAUX
# ========================================
class Service(models.Model):
    """Services médicaux de l'hôpital"""
    name = models.CharField("Nom du service", max_length=255)
    slug = models.SlugField("URL", unique=True, blank=True)
    icon = models.CharField("Icône (Font Awesome)", max_length=50,
                           help_text="Ex: fa-heartbeat, fa-stethoscope")
    short_description = models.CharField("Description courte", max_length=255)
    full_description = CKEditor5Field("Description complète")
    banner_image = models.ImageField("Image bannière", upload_to='services/', blank=True)

    # Détails
    pathologies = models.TextField("Pathologies traitées", blank=True,
                                   help_text="Une par ligne")
    equipment = models.TextField("Équipements disponibles", blank=True,
                                 help_text="Un par ligne")
    admission_conditions = models.TextField("Conditions d'admission", blank=True)
    consultation_hours = models.CharField("Horaires de consultation", max_length=255, blank=True)
    tariffs = models.TextField("Tarifs indicatifs", blank=True)
    contact_phone = models.CharField("Téléphone direct", max_length=20, blank=True)
    show_on_homepage = models.BooleanField(
        "Afficher sur la page d'accueil",
        default=False,
        help_text="Cocher pour afficher ce service sur la page d'accueil (max 6)")

    # Gestion
    display_order = models.IntegerField("Ordre d'affichage", default=0)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service médical"
        verbose_name_plural = "Services médicaux"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ========================================
# IMAGES DES SERVICES (GALERIE)
# ========================================
class ServiceImage(models.Model):
    """Images de galerie pour services"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE,
                               related_name='gallery_images')
    image = models.ImageField("Image", upload_to='services/gallery/')
    caption = models.CharField("Légende", max_length=255, blank=True)
    display_order = models.IntegerField("Ordre", default=0)

    class Meta:
        verbose_name = "Image de service"
        verbose_name_plural = "Images de services"
        ordering = ['display_order']

    def __str__(self):
        return f"{self.service.name} - Image {self.display_order}"


# ========================================
# PERSONNEL MÉDICAL
# ========================================
class Staff(models.Model):
    """Personnel médical de l'hôpital"""
    GRADE_CHOICES = [
        ('Dr', 'Docteur'),
        ('Pr', 'Professeur'),
        ('Inf', 'Infirmier(ère)'),
        ('Tech', 'Technicien(ne)'),
        ('Admin', 'Administratif'),
    ]
    
    # Identité
    first_name = models.CharField("Prénom", max_length=100)
    last_name = models.CharField("Nom", max_length=100)
    photo = models.ImageField("Photo professionnelle", upload_to='staff/')
    grade = models.CharField("Grade", max_length=10, choices=GRADE_CHOICES)
    is_chief = models.BooleanField("Chef de service", default=False)

    # Informations professionnelles
    speciality = models.CharField("Spécialité", max_length=255)
    services = models.ManyToManyField(Service, verbose_name="Services affectés",
                                     related_name='staff_members')
    diplomas = CKEditor5Field("Diplômes", blank=True, help_text="Un par ligne")
    experience = CKEditor5Field("Parcours professionnel", blank=True)
    expertise = CKEditor5Field("Domaines d'expertise", blank=True)
    languages = models.CharField("Langues parlées", max_length=255, blank=True,
                                help_text="Ex: Français, Anglais, Ewondo")
    
    # Rendez-vous
    accepts_appointments = models.BooleanField("Accepte les RDV en ligne", default=False)
    consultation_duration = models.IntegerField("Durée consultation (minutes)", default=30)
    consultation_hours = models.TextField("Horaires de consultation", blank=True,
                                         help_text="Ex: Lundi 8h-12h, Mercredi 14h-18h")
    
    # Contact
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    
    # Gestion
    is_visible = models.BooleanField("Affiché sur le site", default=True)
    display_order = models.IntegerField("Ordre d'affichage", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Membre du personnel"
        verbose_name_plural = "Personnel médical"
        ordering = ['display_order', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_grade_display()} {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ========================================
# CATÉGORIES D'ARTICLES
# ========================================
class Category(models.Model):
    """Catégories pour les actualités"""
    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField("URL", unique=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
    
    def __str__(self):
        return self.name


# ========================================
# ACTUALITÉS (ARTICLES)
# ========================================
class Article(models.Model):
    """Articles d'actualité"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    title = models.CharField("Titre", max_length=255)
    slug = models.SlugField("URL", unique=True, blank=True)
    excerpt = CKEditor5Field("Extrait", blank=True)
    content = CKEditor5Field("Contenu")
    featured_image = models.ImageField("Image principale", upload_to='articles/')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                null=True, verbose_name="Catégorie")
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL,
                              null=True, verbose_name="Auteur")
    
    status = models.CharField("Statut", max_length=10, 
                             choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField("Date de publication", null=True, blank=True)
    meta_description = models.CharField("Description SEO", max_length=160, blank=True)
    
    views_count = models.IntegerField("Nombre de vues", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Actualités"
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ========================================
# IMAGES DES ARTICLES (GALERIE)
# ========================================
class ArticleImage(models.Model):
    """Images de galerie pour articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, 
                               related_name='gallery_images')
    image = models.ImageField("Image", upload_to='articles/gallery/')
    caption = models.CharField("Légende", max_length=255, blank=True)
    display_order = models.IntegerField("Ordre", default=0)
    
    class Meta:
        verbose_name = "Image d'article"
        verbose_name_plural = "Images d'articles"
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.article.title} - Image {self.display_order}"


# ========================================
# CAMPAGNES DE SANTÉ
# ========================================
class Campaign(models.Model):
    """Campagnes de santé publique"""
    STATUS_CHOICES = [
        ('upcoming', 'À venir'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminée'),
    ]
    
    title = models.CharField("Titre", max_length=255)
    slug = models.SlugField("URL", unique=True, blank=True)
    banner_image = models.ImageField("Image bannière", upload_to='campaigns/')

    short_description = models.CharField("Description courte", max_length=255)
    full_description = CKEditor5Field("Description complète")
    
    # Dates et lieu
    start_date = models.DateField("Date de début")
    end_date = models.DateField("Date de fin")
    location = models.CharField("Lieu", max_length=255)
    schedule = models.CharField("Horaires", max_length=255, blank=True,
                               help_text="Ex: 8h-16h")
    
    # Détails
    services_offered = models.TextField("Services offerts", blank=True,
                                       help_text="Un par ligne. Ex: Dépistage gratuit, Vaccination")
    target_audience = models.CharField("Public cible", max_length=255, blank=True)
    objectives = models.TextField("Objectifs de la campagne", blank=True)
    
    # Contact
    contact_name = models.CharField("Responsable", max_length=100, blank=True)
    contact_phone = models.CharField("Téléphone responsable", max_length=20, blank=True)
    
    # Gestion
    registration_enabled = models.BooleanField("Formulaire d'inscription actif", default=False)
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Campagne de santé"
        verbose_name_plural = "Campagnes de santé"
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ========================================
# IMAGES DES CAMPAGNES
# ========================================
class CampaignImage(models.Model):
    """Images de galerie pour campagnes"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE,
                                related_name='gallery_images')
    image = models.ImageField("Image", upload_to='campaigns/gallery/')
    caption = models.CharField("Légende", max_length=255, blank=True)
    display_order = models.IntegerField("Ordre", default=0)
    
    class Meta:
        verbose_name = "Image de campagne"
        verbose_name_plural = "Images de campagnes"
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.campaign.title} - Image {self.display_order}"


# ========================================
# INSCRIPTIONS AUX CAMPAGNES
# ========================================
class CampaignRegistration(models.Model):
    """Inscriptions aux campagnes"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE,
                                related_name='registrations')
    full_name = models.CharField("Nom complet", max_length=255)
    email = models.EmailField("Email")
    phone = models.CharField("Téléphone", max_length=20)
    age = models.IntegerField("Âge", null=True, blank=True)
    reason = models.TextField("Raison de participation", blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inscription à une campagne"
        verbose_name_plural = "Inscriptions aux campagnes"
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.campaign.title}"


# ========================================
# PARTENAIRES
# ========================================
class Partner(models.Model):
    """Partenaires institutionnels"""
    TYPE_CHOICES = [
        ('institutional', 'Institutionnel'),
        ('ngo', 'ONG'),
        ('insurance', 'Mutuelle'),
        ('private', 'Entreprise privée'),
        ('hospital', 'Hôpital partenaire'),
    ]
    
    name = models.CharField("Nom", max_length=255)
    logo = models.ImageField("Logo", upload_to='partners/')
    partner_type = models.CharField("Type", max_length=20, choices=TYPE_CHOICES)
    description = models.TextField("Description", blank=True)
    website = models.URLField("Site web", blank=True)
    collaboration_domain = models.CharField("Domaine de collaboration", 
                                          max_length=255, blank=True)
    
    display_order = models.IntegerField("Ordre d'affichage", default=0)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


# ========================================
# RENDEZ-VOUS
# ========================================
class Appointment(models.Model):
    """Rendez-vous en ligne"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('completed', 'Honoré'),
    ]
    
    # Patient
    patient_name = models.CharField("Nom complet", max_length=255)
    patient_email = models.EmailField("Email")
    patient_phone = models.CharField("Téléphone", max_length=20)
    patient_birthdate = models.DateField("Date de naissance", null=True, blank=True)
    
    # RDV
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Service")
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name="Médecin", related_name='appointments')
    appointment_date = models.DateTimeField("Date et heure du RDV")
    duration = models.IntegerField("Durée (minutes)", default=30)
    
    # Détails
    reason = models.TextField("Motif de consultation")
    is_first_visit = models.BooleanField("Première visite", default=True)
    insurance_number = models.CharField("Numéro d'assurance", max_length=50, blank=True)
    
    # Gestion
    status = models.CharField("Statut", max_length=10, 
                             choices=STATUS_CHOICES, default='pending')
    internal_notes = models.TextField("Notes internes", blank=True)
    created_at = models.DateTimeField("Date de demande", auto_now_add=True)
    
    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.patient_name} - {self.appointment_date.strftime('%d/%m/%Y %H:%M')}"


# ========================================
# MESSAGES DE CONTACT
# ========================================
class ContactMessage(models.Model):
    """Messages via formulaire de contact"""
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('archived', 'Archivé'),
    ]
    
    SUBJECT_CHOICES = [
        ('info', 'Demande d\'information'),
        ('complaint', 'Réclamation'),
        ('suggestion', 'Suggestion'),
        ('partnership', 'Partenariat'),
        ('other', 'Autre'),
    ]
    
    name = models.CharField("Nom", max_length=255)
    email = models.EmailField("Email")
    phone = models.CharField("Téléphone", max_length=20)
    subject = models.CharField("Sujet", max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField("Message")
    
    status = models.CharField("Statut", max_length=10, 
                             choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField("Adresse IP", null=True, blank=True)
    created_at = models.DateTimeField("Date de réception", auto_now_add=True)
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"


# ========================================
# TÉMOIGNAGES
# ========================================
class Testimonial(models.Model):
    """Témoignages de patients"""
    patient_name = models.CharField("Nom du patient", max_length=100)
    patient_photo = models.ImageField("Photo", upload_to='testimonials/', blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, 
                               null=True, blank=True, verbose_name="Service")
    testimonial = models.TextField("Témoignage")
    rating = models.IntegerField("Note", default=5, 
                                help_text="Note sur 5")
    
    is_active = models.BooleanField("Affiché", default=True)
    display_order = models.IntegerField("Ordre d'affichage", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['display_order', '-created_at']
    
    def __str__(self):
        return f"{self.patient_name} - {self.rating}/5"


# ========================================
# ÉQUIPE DE DIRECTION
# ========================================
class DirectionMember(models.Model):
    """Membres de l'équipe de direction"""
    first_name = models.CharField("Prénom", max_length=100)
    last_name = models.CharField("Nom", max_length=100)
    photo = models.ImageField("Photo", upload_to='direction/')
    position = models.CharField("Fonction", max_length=255,
                               help_text="Ex: Directeur Général, Directeur Médical")
    bio = CKEditor5Field("Biographie", blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    
    display_order = models.IntegerField("Ordre d'affichage", default=0)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Membre de direction"
        verbose_name_plural = "Équipe de direction"
        ordering = ['display_order', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"