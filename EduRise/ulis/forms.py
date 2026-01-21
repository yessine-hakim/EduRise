from django import forms

# Institution type (same as enrollment - keep French values for model compatibility)
TYPE_CHOICES = [
    ('Lycée', 'Lycée (High School)'),
    ('Collège', 'Collège (Middle School)'),
    ('Information et orientation', 'Information et orientation (Information and Orientation)'),
    ('Autre', 'Autre (Other)'),
    ('École', 'École (School)'),
    ('Médico-social', 'Médico-social (Medico-Social)'),
    ('EREA', 'EREA'),
]

# Nature label (same as enrollment - keep French values for model compatibility)
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
]

# Public/Private status (same as enrollment)
STATUT_CHOICES = [
    ('Public', 'Public'),
    ('Privé', 'Privé (Private)'),
]

# Restauration (same as enrollment - catering service)
RESTAURATION_CHOICES = [
    (0, 'No'),
    (1, 'Yes'),
]

class ULISForm(forms.Form):
    # Enrollment Data
    Nombre_classes_2024 = forms.IntegerField(
        label="Number of Classes (2024)",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control input-field",
            "placeholder": "Ex: 15"
        })
    )

    Nombre_eleves_2024 = forms.IntegerField(
        label="Number of Students (2024)",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control input-field",
            "placeholder": "Ex: 300"
        })
    )

    # Institution Details
    Type_etablissement = forms.ChoiceField(
        label="Institution Type",
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control input-field"
        })
    )

    libelle_nature = forms.ChoiceField(
        label="Institution Nature",
        choices=NATURE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control input-field"
        })
    )

    Statut_public_prive = forms.ChoiceField(
        label="Public/Private Status",
        choices=STATUT_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control input-field"
        })
    )

    Restauration = forms.ChoiceField(
        label="Restauration",
        choices=RESTAURATION_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control input-field"
        })
    )
 
