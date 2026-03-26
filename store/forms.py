from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "email", "address", "city"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre completo",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "correo@ejemplo.com",
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dirección de entrega",
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ciudad",
            }),
        }
        labels = {
            "full_name": "Nombre completo",
            "email": "Correo electrónico",
            "address": "Dirección",
            "city": "Ciudad",
        }

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if len(full_name) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return full_name

    def clean_city(self):
        city = self.cleaned_data["city"].strip()
        if len(city) < 2:
            raise forms.ValidationError("La ciudad debe tener al menos 2 caracteres.")
        return city

    def clean_address(self):
        address = self.cleaned_data["address"].strip()
        if len(address) < 5:
            raise forms.ValidationError("La dirección debe tener al menos 5 caracteres.")
        return address