from django import forms

class EnrollmentPredictionForm(forms.Form):
    """
    Form to predict enrollment growth of an institution
    """

    # ---------------------------  
    # Number of classes in 2023
    # ---------------------------
    Nombre_classes_2023 = forms.IntegerField(
        label="Number of classes (2023)",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 15'
        }),
        help_text="Total number of classes in the institution"
    )

    # ---------------------------
    # Number of students
    # ---------------------------
    Eleves_Superieur = forms.IntegerField(
        label="Number of students",
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 300'
        }),
        help_text="Total number of students in the institution"
    )

    # ---------------------------
    # Institution type (keep French values for model compatibility)
    # ---------------------------
    TYPE_CHOICES = [
        ('Lycée', 'Lycée (High School)'),
        ('Collège', 'Collège (Middle School)'),
        ('Information et orientation', 'Information et orientation (Information and Orientation)'),
        ('Autre', 'Autre (Other)'),
        ('École', 'École (School)'),
        ('Médico-social', 'Médico-social (Medico-Social)'),
        ('EREA', 'EREA'),
    ]
    Type_etablissement = forms.ChoiceField(
        label="Institution Type",
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # ---------------------------
    # Public/Private status (keep French values for model compatibility)
    # ---------------------------
    STATUT_CHOICES = [
        ('Public', 'Public'),
        ('Privé', 'Privé (Private)'),
    ]
    Statut_public_prive = forms.ChoiceField(
        label="Status (Public/Private)",
        choices=STATUT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # ---------------------------
    # Nature label (keep French values for model compatibility)
    # ---------------------------
    NATURE_CHOICES = [
        ('LYCEE PROFESSIONNEL', 'LYCEE PROFESSIONNEL (Vocational High School)'),
        ('COLLEGE', 'COLLEGE (Middle School)'),
        ('LYCEE POLYVALENT', 'LYCEE POLYVALENT (Comprehensive High School)'),
        ('LYCEE D ENSEIGNEMENT GENERAL', 'LYCEE D ENSEIGNEMENT GENERAL (General Education High School)'),
        ('LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE', 'LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE (General and Technical Education High School)'),
        ('SECTION D ENSEIGNEMENT PROFESSIONNEL', 'SECTION D ENSEIGNEMENT PROFESSIONNEL (Vocational Education Section)'),
        ('CENTRE D INFORMATION ET D ORIENTATION', 'CENTRE D INFORMATION ET D ORIENTATION (Information and Orientation Center)'),
        ('SECTION ENSEIGT GEN. ET PROF. ADAPTE', 'SECTION ENSEIGT GEN. ET PROF. ADAPTE (Adapted General and Professional Education Section)'),
        ('LYCEE ENS GENERAL TECHNO PROF AGRICOLE', 'LYCEE ENS GENERAL TECHNO PROF AGRICOLE (General Technical and Agricultural High School)'),
        ('CIRCONSCRIPTIONS INSPECTION EDUC NAT', 'CIRCONSCRIPTIONS INSPECTION EDUC NAT (Educational Inspection Districts)'),
        ('ECOLE DE NIVEAU ELEMENTAIRE', 'ECOLE DE NIVEAU ELEMENTAIRE (Elementary Level School)'),
        ('ECOLE MATERNELLE', 'ECOLE MATERNELLE (Nursery School)'),
        ('INSTITUT MEDICO-EDUCATIF', 'INSTITUT MEDICO-EDUCATIF (Medico-Educational Institute)'),
        ('INSTITUT THERAPEUT. EDUCATIF PEDAGOGIQUE', 'INSTITUT THERAPEUT. EDUCATIF PEDAGOGIQUE (Therapeutic Educational Pedagogical Institute)'),
        ('ETAB REGIONAL/LYCEE ENSEIGNEMENT ADAPTE', 'ETAB REGIONAL/LYCEE ENSEIGNEMENT ADAPTE (Regional Establishment/Adapted Education High School)'),
        ('ECOLE ELEMENTAIRE D APPLICATION', 'ECOLE ELEMENTAIRE D APPLICATION (Application Elementary School)'),
        ('MAISON FAMILIALE RURALE EDUCATION ORIENT', 'MAISON FAMILIALE RURALE EDUCATION ORIENT (Rural Family Home Education Orientation)'),
        ('SERVICE DE LA DSDEN', 'SERVICE DE LA DSDEN (DSDEN Service)'),
        ('ETABLISSEMENT POUR POLY-HANDICAPES', 'ETABLISSEMENT POUR POLY-HANDICAPES (Establishment for Multiple Disabilities)'),
        ('DIRECTION SERVICES DEPARTEMENTAUX EN', 'DIRECTION SERVICES DEPARTEMENTAUX EN (Departmental Services Direction EN)'),
        ('ECOLE MATERNELLE D APPLICATION', 'ECOLE MATERNELLE D APPLICATION (Application Nursery School)'),
        ('LYCEE EXPERIMENTAL', 'LYCEE EXPERIMENTAL (Experimental High School)'),
        ('COLLEGE EXPERIMENTAL', 'COLLEGE EXPERIMENTAL (Experimental Middle School)'),
        ('IES POUR DEFICIENTS VISUELS', 'IES POUR DEFICIENTS VISUELS (Institute for Visually Impaired)'),
        ('LYCEE D ENSEIGNEMENT TECHNOLOGIQUE', 'LYCEE D ENSEIGNEMENT TECHNOLOGIQUE (Technical Education High School)'),
        ('INSTITUT EDUCATION MOTRICE (IEM)', 'INSTITUT EDUCATION MOTRICE (IEM) (Motor Education Institute)'),
        ('SECTION ENSEIGT GENERAL ET TECHNOLOGIQUE', 'SECTION ENSEIGT GENERAL ET TECHNOLOGIQUE (General and Technical Education Section)'),
        ('ECOLE PROFESSIONNELLE SPECIALISEE', 'ECOLE PROFESSIONNELLE SPECIALISEE (Specialized Vocational School)'),
        ('ECOLE SECONDAIRE SPECIALISEE (2 D CYCLE)', 'ECOLE SECONDAIRE SPECIALISEE (2 D CYCLE) (Specialized Secondary School 2nd Cycle)'),
        ('ETABLISSEMENT MEDICO-EXPERIMENTAL', 'ETABLISSEMENT MEDICO-EXPERIMENTAL (Medico-Experimental Establishment)'),
        ('LYCEE CLIMATIQUE', 'LYCEE CLIMATIQUE (Climate High School)'),
        ('LYCEE ENS GENERAL TECHNO PROF AGRICOLE', 'LYCEE ENS GENERAL TECHNO PROF AGRICOLE (General Technical and Agricultural High School)'),
        ('LYCEE EXPERIMENTAL', 'LYCEE EXPERIMENTAL (Experimental High School)'),
        # Add other unique values here if missing
    ]
    libelle_nature = forms.ChoiceField(
        label="Institution Nature",
        choices=NATURE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # ---------------------------
    # Accommodation (keep French values for model compatibility)
    # ---------------------------
    HEBERGEMENT_CHOICES = [
        (0, 'No'),
        (1, 'Yes'),
    ]
    Hebergement = forms.ChoiceField(
        label="Accommodation Type",
        choices=HEBERGEMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # ---------------------------
    # Latitude (required for clustering)
    # ---------------------------
    latitude = forms.FloatField(
        label="Latitude",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 48.8566',
            'step': '0.000001'
        }),
        help_text="Geographic latitude coordinate (optional, defaults to Paris)"
    )

    # ---------------------------
    # Longitude (required for clustering)
    # ---------------------------
    longitude = forms.FloatField(
        label="Longitude",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 2.3522',
            'step': '0.000001'
        }),
        help_text="Geographic longitude coordinate (optional, defaults to Paris)"
    )

    # ---------------------------
    # Restauration (required for clustering)
    # ---------------------------
    RESTAURATION_CHOICES = [
        (0, 'No'),
        (1, 'Yes'),
    ]
    Restauration = forms.ChoiceField(
        label="Catering Service",
        choices=RESTAURATION_CHOICES,
        required=False,
        initial=0,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Whether the institution provides catering services"
    )

    # ---------------------------
    # ULIS (required for clustering)
    # ---------------------------
    ULIS_CHOICES = [
        (0, 'No'),
        (1, 'Yes'),
    ]
    ULIS = forms.ChoiceField(
        label="ULIS (Inclusive Education Units)",
        choices=ULIS_CHOICES,
        required=False,
        initial=0,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Whether the institution has ULIS units for students with disabilities"
    )
 
