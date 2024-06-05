# forms.py
from django import forms
from .models import Usuario


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['name', 'email', 'phone', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
