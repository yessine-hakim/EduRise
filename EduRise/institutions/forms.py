from django import forms
from services.encoder_loader import get_encoder_loader
import logging

logger = logging.getLogger(__name__)


class InstitutionsPredictionForm(forms.Form):
    """Form to collect features for predicting Nombre_eleves_2024."""

    nombre_classes_2024 = forms.FloatField(
        label='Number of Classes (2024)',
        min_value=0.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 20'})
    )

    code_departement = forms.ChoiceField(
        label='Department Code',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    type_etablissement = forms.ChoiceField(
        label='Establishment Type',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    statut_public_prive = forms.ChoiceField(
        label='Public/Private Status',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    latitude = forms.FloatField(
        label='Latitude',
        min_value=-90.0,
        max_value=90.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'})
    )

    longitude = forms.FloatField(
        label='Longitude',
        min_value=-180.0,
        max_value=180.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'})
    )

    RESTAURATION_CHOICES = [(0, 'No'), (1, 'Yes')]
    HEB_CHOICES = [(0, 'No'), (1, 'Yes')]
    ULIS_CHOICES = [(0, 'No'), (1, 'Yes')]

    restauration = forms.ChoiceField(
        label='Restauration',
        choices=RESTAURATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    hebergement = forms.ChoiceField(
        label='Hebergement',
        choices=HEB_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    ulis = forms.ChoiceField(
        label='ULIS',
        choices=ULIS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            encoder_loader = get_encoder_loader()
            self.fields['code_departement'].choices = encoder_loader.get_choices('Code_departement')
            self.fields['type_etablissement'].choices = encoder_loader.get_choices('Type_etablissement')
            self.fields['statut_public_prive'].choices = encoder_loader.get_choices('Statut_public_prive')
        except Exception as e:
            logger.error(f"Error loading encoder choices for InstitutionsPredictionForm: {e}")
            self.fields['code_departement'].choices = [('', 'Error loading choices')]
            self.fields['type_etablissement'].choices = [('', 'Error loading choices')]
            self.fields['statut_public_prive'].choices = [('', 'Error loading choices')]

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['nombre_classes_2024', 'code_departement', 'type_etablissement', 'statut_public_prive', 'latitude', 'longitude', 'restauration', 'hebergement', 'ulis']
        for field in required_fields:
            if field not in cleaned_data or cleaned_data[field] in [None, '']:
                raise forms.ValidationError(f'Field {field} is required.')
        return cleaned_data

    def get_feature_vector(self, feature_order=None):
        """Return a feature vector (list) in the provided feature_order or a default order."""
        if not self.is_valid():
            raise ValueError('Form must be valid to extract features')
        encoder_loader = get_encoder_loader()
        # Encode categorical values
        code_dep_encoded = encoder_loader.encode('Code_departement', self.cleaned_data['code_departement'])
        type_encoded = encoder_loader.encode('Type_etablissement', self.cleaned_data['type_etablissement'])
        statut_encoded = encoder_loader.encode('Statut_public_prive', self.cleaned_data['statut_public_prive'])

        feature_map = {
            'Nombre_classes_2024': float(self.cleaned_data['nombre_classes_2024']),
            'Code_departement': int(code_dep_encoded),
            'Type_etablissement': int(type_encoded),
            'Statut_public_prive': int(statut_encoded),
            'latitude': float(self.cleaned_data['latitude']),
            'longitude': float(self.cleaned_data['longitude']),
            'Restauration': int(self.cleaned_data['restauration']),
            'Hebergement': int(self.cleaned_data['hebergement']),
            'ULIS': int(self.cleaned_data['ulis']),
        }

        if feature_order:
            return [feature_map[f] for f in feature_order]
        # Default order
        default_order = ['Nombre_classes_2024', 'Code_departement', 'Type_etablissement', 'Statut_public_prive', 'latitude', 'longitude', 'Restauration', 'Hebergement', 'ULIS']
        return [feature_map[f] for f in default_order
] 
