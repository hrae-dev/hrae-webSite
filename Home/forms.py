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
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre nom complet'
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'votre.email@exemple.com'
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': '+237 6XX XXX XXX'
            }),
            'patient_birthdate': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'service': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'staff': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'appointment_date': forms.HiddenInput(attrs={
                'id': 'id_appointment_date',
                'required': 'required'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Décrivez le motif de votre consultation'
            }),
            'is_first_visit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }, choices=[(True, 'Oui'), (False, 'Non')]),
            'insurance_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Numéro d\'assurance (optionnel)'
            }),
        }
        labels = {
            'patient_name': 'Nom complet *',
            'patient_email': 'Email *',
            'patient_phone': 'Téléphone *',
            'patient_birthdate': 'Date de naissance',
            'service': 'Service médical *',
            'staff': 'Médecin (optionnel)',
            'appointment_date': 'Date et heure souhaitée *',
            'reason': 'Motif de consultation *',
            'is_first_visit': 'Première visite ? *',
            'insurance_number': 'Numéro d\'assurance',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer seulement les médecins qui acceptent les RDV
        self.fields['staff'].queryset = self.fields['staff'].queryset.filter(
            accepts_appointments=True
        )
        self.fields['staff'].required = False
        self.fields['patient_birthdate'].required = False
        self.fields['insurance_number'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        staff = cleaned_data.get('staff')
        
        # Si un médecin est sélectionné, vérifier qu'il appartient au service
        if staff and service:
            if service not in staff.services.all():
                raise forms.ValidationError(
                    f"Le médecin {staff} ne travaille pas dans le service {service}."
                )
        
        return cleaned_data

class CampaignRegistrationForm(forms.ModelForm):
    class Meta:
        model = CampaignRegistration
        fields = ['full_name', 'email', 'phone', 'age', 'reason']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'age': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'reason': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3}),
        }
class ContactMessageForm(forms.ModelForm):
    """Formulaire de contact"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'votre.email@exemple.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': '+237 6XX XXX XXX'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Votre message...'
            }),
        }
        labels = {
            'name': 'Nom complet *',
            'email': 'Email *',
            'phone': 'Téléphone *',
            'subject': 'Sujet *',
            'message': 'Votre message *',
        }