from django import forms
from .models import Patient, Doctor

class PatientPhotoForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['photo']

class DoctorPhotoForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['photo'] 