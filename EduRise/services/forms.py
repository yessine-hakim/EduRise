from django import forms
from .encoder_loader import get_encoder_loader
import logging

logger = logging.getLogger(__name__)


class ServicesPredictionForm(forms.Form):
    """
    Form for predicting Restauration or Hebergement services.
    
    This form collects 9 features required by the ML classification models.
    Categorical features use dropdown selectors populated from LabelEncoders.
    Encoding happens at form submission time using the get_feature_array() method.
    
    Model Features (in order):
    1. Code_departement (numeric)
    2. Nombre_Eleves_Totale (numeric)
    3. Type_etablissement (categorical - dropdown)
    4. Statut_public_prive (categorical - dropdown)
    5. libelle_nature (categorical - dropdown)
    6. latitude (numeric)
    7. Code_region (numeric)
    8. ULIS (binary)
    9. Eleves_per_class_last (numeric)
    """
    
    # Model selection - determines which classifier to use
    MODEL_CHOICES = [
        ('restauration', 'Restauration'),
        ('hebergement', 'Hebergement'),
    ]
    
    model_type = forms.ChoiceField(
        choices=MODEL_CHOICES,
        label='Service Type',
        help_text='Select the service to predict',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Feature 1: Code_departement (numeric)
    code_departement = forms.IntegerField(
        label='Department Code',
        help_text='Numeric code of the department (e.g., 75 for Paris)',
        min_value=1,
        max_value=999,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 75'
        })
    )
    
    # Feature 2: Nombre_Eleves_Totale (numeric)
    nombre_eleves_totale = forms.IntegerField(
        label='Total Number of Students',
        help_text='Total student enrollment',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 500'
        })
    )
    
    # Feature 3: Type_etablissement (categorical - dropdown)
    type_etablissement = forms.ChoiceField(
        label='Establishment Type',
        help_text='Select the type of establishment',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]  # Will be populated in __init__
    )
    
    # Feature 4: Statut_public_prive (categorical - dropdown)
    statut_public_prive = forms.ChoiceField(
        label='Public/Private Status',
        help_text='Select whether the institution is public or private',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]  # Will be populated in __init__
    )
    
    # Feature 5: libelle_nature (categorical - dropdown)
    libelle_nature = forms.ChoiceField(
        label='Nature Label',
        help_text='Select the nature/type of the institution',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]  # Will be populated in __init__
    )
    
    # Feature 6: latitude (numeric)
    latitude = forms.FloatField(
        label='Latitude',
        help_text='Geographic latitude coordinate (e.g., 48.8566 for Paris)',
        min_value=-90.0,
        max_value=90.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 48.8566',
            'step': '0.0001'
        })
    )
    
    # Feature 7: Code_region (numeric)
    code_region = forms.IntegerField(
        label='Region Code',
        help_text='Numeric code of the region',
        min_value=1,
        max_value=99,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 11'
        })
    )
    
    # Feature 8: ULIS (binary)
    ULIS_CHOICES = [
        (0, 'No'),
        (1, 'Yes'),
    ]
    
    ulis = forms.ChoiceField(
        label='ULIS',
        help_text='Does the institution have ULIS?',
        choices=ULIS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Feature 9: Eleves_per_class_last (numeric)
    eleves_per_class_last = forms.FloatField(
        label='Students per Class',
        help_text='Average number of students per class',
        min_value=0.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 25.5',
            'step': '0.1'
        })
    )
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form and populate categorical field choices from encoders.
        """
        super().__init__(*args, **kwargs)
        
        try:
            # Load the encoder loader
            encoder_loader = get_encoder_loader()
            
            # Populate Type_etablissement choices
            self.fields['type_etablissement'].choices = encoder_loader.get_choices('Type_etablissement')
            logger.info(f"Loaded {len(self.fields['type_etablissement'].choices)} choices for Type_etablissement")
            
            # Populate Statut_public_prive choices
            self.fields['statut_public_prive'].choices = encoder_loader.get_choices('Statut_public_prive')
            logger.info(f"Loaded {len(self.fields['statut_public_prive'].choices)} choices for Statut_public_prive")
            
            # Populate libelle_nature choices
            self.fields['libelle_nature'].choices = encoder_loader.get_choices('libelle_nature')
            logger.info(f"Loaded {len(self.fields['libelle_nature'].choices)} choices for libelle_nature")
            
        except Exception as e:
            logger.error(f"Error loading encoder choices: {e}")
            # Set empty choices if encoders fail to load
            self.fields['type_etablissement'].choices = [('', 'Error loading choices')]
            self.fields['statut_public_prive'].choices = [('', 'Error loading choices')]
            self.fields['libelle_nature'].choices = [('', 'Error loading choices')]
    
    def clean(self):
        """
        Validate the entire form and ensure all required fields are present.
        """
        cleaned_data = super().clean()
        
        # Ensure all required fields are present
        required_fields = [
            'code_departement', 'nombre_eleves_totale', 'type_etablissement',
            'statut_public_prive', 'libelle_nature', 'latitude',
            'code_region', 'ulis', 'eleves_per_class_last'
        ]
        
        for field in required_fields:
            if field not in cleaned_data or cleaned_data[field] is None:
                raise forms.ValidationError(f'Field {field} is required.')
        
        return cleaned_data
    
    def get_feature_array(self):
        """
        Extract form data and return as a list in the correct feature order.
        
        This method returns raw values (strings for categoricals) to be encoded by the backend.
        
        CRITICAL: The order must match exactly what the models expect:
        [Code_departement, Nombre_Eleves_Totale, Type_etablissement, 
         Statut_public_prive, libelle_nature, latitude, Code_region, 
         ULIS, Eleves_per_class_last]
        
        Returns:
            list: Feature values in the correct order for model prediction
            
        Raises:
            ValueError: If form is not valid
        """
        if not self.is_valid():
            raise ValueError("Form must be valid before extracting features")
        
        try:
            # Convert ULIS to integer (it comes as string from ChoiceField)
            ulis_value = int(self.cleaned_data['ulis'])
            
            # Extract features in the exact order expected by the models
            # We strictly pass raw strings for categoricals now
            features = [
                self.cleaned_data['code_departement'],
                self.cleaned_data['nombre_eleves_totale'],
                self.cleaned_data['type_etablissement'],  # Raw string
                self.cleaned_data['statut_public_prive'], # Raw string
                self.cleaned_data['libelle_nature'],      # Raw string
                self.cleaned_data['latitude'],
                self.cleaned_data['code_region'],
                ulis_value,
                self.cleaned_data['eleves_per_class_last'],
            ]
            
            logger.info(f"Feature payload (raw): {features}")
            return features
            
        except Exception as e:
            logger.error(f"Error preparing feature payload: {e}")
            raise e

class ClusteringForm(forms.Form):
    """
    Form for predicting service importance clusters.
    
    Model Features:
    1. libelle_nature (categorical)
    2. Restauration (binary)
    3. Hebergement (binary)
    4. Inst_rest_pressure (numeric)
    5. Inst_heberg_pressure (numeric)
    """
    
    # Feature: Code Department
    code_departement = forms.IntegerField(
        label='Department Code',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 75'})
    )

    # Feature: Type Etablissement
    type_etablissement = forms.ChoiceField(
        label='Establishment Type',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )

    # Feature: Statut Public/Prive
    statut_public_prive = forms.ChoiceField(
        label='Status (Public/Private)',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )

    # Feature: Code Region
    code_region = forms.IntegerField(
        label='Region Code',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 11'})
    )

    # Feature: Nature Label
    libelle_nature = forms.ChoiceField(
        label='Nature Label',
        help_text='Select the nature/type of the institution',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[] 
    )
    
    # Feature 2: Restauration
    restauration = forms.ChoiceField(
        label='Restauration Service',
        help_text='Does the institution offer restauration?',
        choices=[(0, 'No'), (1, 'Yes')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Feature 3: Hebergement
    hebergement = forms.ChoiceField(
        label='Accommodation Service',
        help_text='Does the institution offer accommodation?',
        choices=[(0, 'No'), (1, 'Yes')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Feature 4: Student Count
    nombre_eleves = forms.FloatField(
        label='Total Number of Students',
        help_text='Total number of students in the institution',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            encoder_loader = get_encoder_loader()
            self.fields['libelle_nature'].choices = encoder_loader.get_choices('libelle_nature')
            self.fields['type_etablissement'].choices = encoder_loader.get_choices('Type_etablissement')
            self.fields['statut_public_prive'].choices = encoder_loader.get_choices('Statut_public_prive')
        except Exception as e:
            logger.error(f"Error loading encoder choices for ClusteringForm: {e}")
            self.fields['libelle_nature'].choices = [('', 'Error loading choices')]
            self.fields['type_etablissement'].choices = [('', 'Error loading choices')]
            self.fields['statut_public_prive'].choices = [('', 'Error loading choices')]

    def get_encoded_features(self):
        """
        Prepare features for the clustering model.
        Calculates pressure indices. 
        Note: Categorical encoding for 'libelle_nature' is handled by the HF backend.
        """
        if not self.is_valid():
            raise ValueError("Form is invalid")
            
        # Get cleaned data
        nombre_eleves = self.cleaned_data['nombre_eleves']
        restauration = int(self.cleaned_data['restauration'])
        hebergement = int(self.cleaned_data['hebergement'])
        
        # Calculate Pressure
        inst_rest_pressure = nombre_eleves * restauration
        inst_heberg_pressure = nombre_eleves * hebergement
        
        features = {
            "Restauration": float(restauration),
            "Hebergement": float(hebergement),
            "Inst_rest_pressure": float(inst_rest_pressure),
            "Inst_heberg_pressure": float(inst_heberg_pressure),
            # Pass through raw values
            "Code_departement": float(self.cleaned_data['code_departement']),
            "Code_region": float(self.cleaned_data['code_region']),
            "Nombre_eleves": float(nombre_eleves),
            # Send nature as STRING to be encoded by backend
            "libelle_nature": self.cleaned_data['libelle_nature']
        }

        # Include other categoricals as needed - checking if backend expects them
        # Currently app.py only processes libelle_nature for clustering, 
        # but we can send others if future proofing.
        # For now, let's just send what we have.
        
        return features

 
