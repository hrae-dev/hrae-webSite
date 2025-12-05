from django import forms
from .models import Appointment, ContactMessage, CampaignRegistration


class AppointmentForm(forms.ModelForm):
    """Formulaire de prise de rendez-vous"""
    
    class Meta:
        model = Appointment
        fields = [
            'patient_name', 'patient_email', 'patient_phone', 'patient_birthdate',
            'service', 'staff', 'appointment_date', 'reason', 
            'is_first_visit', 'insurance_number'
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre nom complet'
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'votre.email@exemple.com'
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+237 6XX XXX XXX'
            }),
            'patient_birthdate': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'service': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'id': 'id_service'
            }),
            'staff': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'id': 'id_staff'
            }),
            'appointment_date': forms.DateTimeInput(attrs={
                'type': 'hidden',
                'id': 'id_appointment_date'
            }, format='%Y-%m-%dT%H:%M:%S'),
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Décrivez le motif de votre consultation'
            }),
            'is_first_visit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }, choices=[(True, 'Oui, première visite'), (False, 'Non, patient existant')]),
            'insurance_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Numéro d\'assurance (optionnel)'
            }),
        }
        labels = {
            'patient_name': 'Nom complet',
            'patient_email': 'Adresse email',
            'patient_phone': 'Téléphone',
            'patient_birthdate': 'Date de naissance',
            'service': 'Service médical',
            'staff': 'Médecin souhaité',
            'appointment_date': 'Date et heure souhaitées',
            'reason': 'Motif de consultation',
            'is_first_visit': 'Première visite ?',
            'insurance_number': 'Numéro d\'assurance',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer seulement les médecins qui acceptent les RDV
        self.fields['staff'].queryset = self.fields['staff'].queryset.filter(
            accepts_appointments=True
        )
        self.fields['staff'].required = False
        self.fields['staff'].empty_label = "-- Pas de préférence --"
        self.fields['patient_birthdate'].required = False
        self.fields['insurance_number'].required = False

        # IMPORTANT: Ne pas ajouter l'attribut HTML 'required' car le formulaire multi-étapes
        # cache les champs avec display:none, ce qui empêche la validation HTML5 de fonctionner.
        # Django fera la validation côté serveur.
    
    def clean(self):
        cleaned_data = super().clean()
        # Validation supprimée : permettre de sélectionner n'importe quel médecin
        # même s'il ne travaille pas dans le service sélectionné
        return cleaned_data


class CampaignRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription aux campagnes de santé"""
    
    class Meta:
        model = CampaignRegistration
        fields = ['full_name', 'email', 'phone', 'age', 'reason']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'votre.email@exemple.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': '+237 6XX XXX XXX'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Votre âge',
                'min': '0',
                'max': '120'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'rows': 3,
                'placeholder': 'Pourquoi souhaitez-vous participer à cette campagne ?'
            }),
        }
        labels = {
            'full_name': 'Nom complet',
            'email': 'Adresse email',
            'phone': 'Téléphone',
            'age': 'Âge',
            'reason': 'Raison de participation',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['reason'].required = False
        
        # Champs requis
        required_fields = ['full_name', 'email', 'phone']
        for field_name in required_fields:
            self.fields[field_name].widget.attrs['required'] = 'required'


class ContactMessageForm(forms.ModelForm):
    """Formulaire de contact"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'votre.email@exemple.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+237 6XX XXX XXX'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 6,
                'placeholder': 'Écrivez votre message ici...'
            }),
        }
        labels = {
            'name': 'Nom complet *',
            'email': 'Adresse email *',
            'phone': 'Téléphone *',
            'subject': 'Sujet *',
            'message': 'Votre message *',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tous les champs sont requis
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['required'] = 'required'