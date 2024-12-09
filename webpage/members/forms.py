# members/forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput, label="Leave empty")  # Honeypot field