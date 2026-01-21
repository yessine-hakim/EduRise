from django import forms
from .models import Institution


class InstitutionForm(forms.ModelForm):
    """Form for adding new institutions."""
    
    class Meta:
        model = Institution
        fields = [
            'name',
            'nombre_classes_2009',
            'eleves_premier',
            'eleves_superieur',
            'latitude',
            'longitude'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional institution name'
            }),
            'nombre_classes_2009': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10',
                'step': '0.1',
                'min': '0'
            }),
            'eleves_premier': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 150',
                'step': '0.1',
                'min': '0'
            }),
            'eleves_superieur': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 200',
                'step': '0.1',
                'min': '0'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 48.8566',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2.3522',
                'step': 'any'
            }),
        }


class ClassificationForm(forms.Form):
    """Form for predicting if an institution is public or private."""
    
    nombre_classes_2009 = forms.FloatField(
        label='Number of Classes (2009)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'placeholder': 'e.g., 10'
        })
    )
    
    eleves_premier = forms.FloatField(
        label='Primary Students',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1',
            'min': '0',
            'placeholder': 'e.g., 150'
        })
    )
    
    eleves_superieur = forms.FloatField(
        label='Secondary Students',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1',
            'min': '0',
            'placeholder': 'e.g., 200'
        })
    )
    
    latitude = forms.FloatField(
        label='Latitude',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.0001',
            'placeholder': 'e.g., 48.8566'
        })
    )
    
    longitude = forms.FloatField(
        label='Longitude',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.0001',
            'placeholder': 'e.g., 2.3522'
        })
    )
    
    # Binary features
    restauration = forms.ChoiceField(
        label='Restauration',
        choices=[(0, 'No'), (1, 'Yes')],
        initial=0,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    hebergement = forms.ChoiceField(
        label='Hebergement (Boarding)',
        choices=[(0, 'No'), (1, 'Yes')],
        initial=0,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ulis = forms.ChoiceField(
        label='ULIS (Special Needs)',
        choices=[(0, 'No'), (1, 'Yes')],
        initial=0,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
 
