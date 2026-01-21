"""
Encoder Loader for Services Classification

This module handles managing categorical feature mappings for 
Services classification models (Restauration and Hebergement).

Refactored to use static mappings instead of loading joblib objects at runtime
to reduce memory usage and improve deployment stability.
"""

import logging

logger = logging.getLogger(__name__)

# Static mappings for categorical features
# These were extracted from the original LabelEncoder .joblib files
ENCODER_MAPPINGS = {
    "Type_etablissement": [
        "Autre",
        "Collège",
        "EREA",
        "Information et orientation",
        "Lycée",
        "Médico-social",
        "École"
    ],
    "Statut_public_prive": [
        "Privé",
        "Public"
    ],
    "libelle_nature": [
        "ADMINISTRATION CENTRALE",
        "CENTRE D INFORMATION ET D ORIENTATION",
        "CIRCONSCRIPTIONS INSPECTION EDUC NAT",
        "COLLEGE",
        "COLLEGE CLIMATIQUE",
        "COLLEGE EXPERIMENTAL",
        "COLLEGE SPECIALISE",
        "DIRECTION SERVICES DEPARTEMENTAUX EN",
        "ECOLE DE NIVEAU ELEMENTAIRE",
        "ECOLE DE NIVEAU ELEMENTAIRE SPECIALISEE",
        "ECOLE DE PLEIN AIR",
        "ECOLE ELEMENTAIRE D APPLICATION",
        "ECOLE MATERNELLE",
        "ECOLE MATERNELLE D APPLICATION",
        "ECOLE PRIMAIRE FRANCAISE A L ETRANGER",
        "ECOLE PROFESSIONNELLE SPECIALISEE",
        "ECOLE REGIONALE DU PREMIER DEGRE",
        "ECOLE SANS EFFECTIFS PERMANENTS",
        "ECOLE SECONDAIRE SPECIALISEE (2 D CYCLE)",
        "ECOLES COMPOSEES UNIQT DE STS ET OU CPGE",
        "ETAB REGIONAL/LYCEE ENSEIGNEMENT ADAPTE",
        "ETABLISSEMENT DE REINSERTION SCOLAIRE",
        "ETABLISSEMENT MEDICO-EXPERIMENTAL",
        "ETABLISSEMENT POUR POLY-HANDICAPES",
        "IES POUR DEFICIENTS AUDITIFS",
        "IES POUR DEFICIENTS VISUELS",
        "IES POUR SOURDS-AVEUGLES",
        "INSTITUT EDUCATION MOTRICE (IEM)",
        "INSTITUT MEDICO-EDUCATIF",
        "INSTITUT THERAPEUT. EDUCATIF PEDAGOGIQUE",
        "LYCEE CLIMATIQUE",
        "LYCEE D ENSEIGNEMENT GENERAL",
        "LYCEE D ENSEIGNEMENT TECHNOLOGIQUE",
        "LYCEE ENS GENERAL TECHNO PROF AGRICOLE",
        "LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE",
        "LYCEE EXPERIMENTAL",
        "LYCEE POLYVALENT",
        "LYCEE PROFESSIONNEL",
        "MAISON FAMILIALE RURALE EDUCATION ORIENT",
        "RECTORAT",
        "SECTION D ENSEIGNEMENT PROFESSIONNEL",
        "SECTION ENSEIGNT GEN. ET PROF. ADAPTE",
        "SECTION ENSEIGT GENERAL ET TECHNOLOGIQUE",
        "SERVICE DE LA DSDEN",
        "SERVICE RECTORAL"
    ],
    "Code_departement": [
        "001", "002", "003", "004", "005", "006", "007", "008", "009", "010",
        "011", "012", "013", "014", "015", "016", "017", "018", "019", "021",
        "022", "023", "024", "025", "026", "027", "028", "029", "02A", "02B",
        "030", "031", "032", "033", "034", "035", "036", "037", "038", "039",
        "040", "041", "042", "043", "044", "045", "046", "047", "048", "049",
        "050", "051", "052", "053", "054", "055", "056", "057", "058", "059",
        "060", "061", "062", "063", "064", "065", "066", "067", "068", "069",
        "070", "071", "072", "073", "074", "075", "076", "077", "078", "079",
        "080", "081", "082", "083", "084", "085", "086", "087", "088", "089",
        "090", "091", "092", "093", "094", "095", "971", "972", "973", "974", "976"
    ]
}


class MockLabelEncoder:
    """
    Mock class that mimics the behavior of sklearn's LabelEncoder.
    Only implements the required methods for our use case.
    """
    def __init__(self, classes):
        self.classes_ = classes
        self._class_to_index = {cls: idx for idx, cls in enumerate(classes)}

    def transform(self, values):
        """Encode a list of values."""
        return [self._class_to_index[v] for v in values]


class EncoderLoader:
    """
    Singleton class to manage categorical features using static mappings.
    """
    
    _instance = None
    _encoders_init = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EncoderLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the encoder loader with static mappings."""
        if not EncoderLoader._encoders_init:
            self.encoders = {}
            for feature, classes in ENCODER_MAPPINGS.items():
                self.encoders[feature] = MockLabelEncoder(classes)
            EncoderLoader._encoders_init = True
            logger.info(f"Initialized EncoderLoader with {len(self.encoders)} static mappings")
    
    def get_encoder(self, feature_name):
        """
        Get the mock encoder for a specific feature.
        """
        if feature_name not in self.encoders:
            raise KeyError(f"Encoder mapping not found for feature: {feature_name}")
        return self.encoders[feature_name]
    
    def get_classes(self, feature_name):
        """
        Get the valid classes for a categorical feature.
        """
        encoder = self.get_encoder(feature_name)
        return list(encoder.classes_)
    
    def get_choices(self, feature_name):
        """
        Get choices in Django form format: [(value, label), ...]
        """
        classes = self.get_classes(feature_name)
        return [(cls, cls) for cls in classes]
    
    def encode(self, feature_name, value):
        """
        Encode a categorical value using the static mapping.
        """
        encoder = self.get_encoder(feature_name)
        
        if value not in encoder._class_to_index:
            raise ValueError(
                f"Value '{value}' not found in mappings for {feature_name}. "
                f"Valid values: {list(encoder.classes_[:10])}..."
            )
        
        return int(encoder.transform([value])[0])
    
    def get_available_encoders(self):
        """
        Get list of all available feature names.
        """
        return list(self.encoders.keys())
    
    def is_categorical(self, feature_name):
        """
        Check if a feature is categorical.
        """
        return feature_name in self.encoders


# Create a global instance
_encoder_loader = None


def get_encoder_loader():
    """
    Get the singleton instance of EncoderLoader.
    """
    global _encoder_loader
    if _encoder_loader is None:
        _encoder_loader = EncoderLoader()
    return _encoder_loader
 
