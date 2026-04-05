from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import WebmartUser, phone_regex


class RegistrationForm(UserCreationForm):
    """Registration form with email, phone, and date of birth."""
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=13, required=False, validators=[phone_regex])
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = WebmartUser
        fields = ['username', 'email', 'phone', 'date_of_birth', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        if not email and not phone:
            raise forms.ValidationError('Either email or phone number is required.')
        return cleaned_data