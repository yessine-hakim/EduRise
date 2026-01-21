import os
import json
import joblib
import numpy as np
from pathlib import Path
from django.conf import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ======================================================
# KNN MODEL CONFIG
# ======================================================
# Path to the KNN model file - using absolute path for reliability
ULIS_APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ULIS_APP_DIR, 'models', 'knn_uliss_model.joblib')

logger.info(f"KNN Model path: {MODEL_PATH}")
logger.info(f"Model file exists: {os.path.exists(MODEL_PATH)}")

# Load model at startup
try:
    if os.path.exists(MODEL_PATH):
        KNN_MODEL = joblib.load(MODEL_PATH)
        MODEL_LOADED = True
        logger.info(f"✓ KNN ULIS model loaded successfully from {MODEL_PATH}")
    else:
        logger.error(f"Model file not found at {MODEL_PATH}")
        MODEL_LOADED = False
        KNN_MODEL = None
except Exception as e:
    MODEL_LOADED = False
    logger.error(f"✗ Failed to load KNN model: {e}")
    import traceback
    traceback.print_exc()
    KNN_MODEL = None

# ======================================================
# MAPPINGS FOR FORM VALUES TO INTEGERS
# ======================================================
TYPE_ETABLISSEMENT_MAPPING = {
    'Lycée': 0,
    'Collège': 1,
    'Information et orientation': 2,
    'Autre': 3,
    'École': 4,
    'Médico-social': 5,
    'EREA': 6,
}

LIBELLE_NATURE_MAPPING = {
    'LYCEE PROFESSIONNEL': 0,
    'COLLEGE': 1,
    'LYCEE POLYVALENT': 2,
    'LYCEE D ENSEIGNEMENT GENERAL': 3,
    'LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE': 4,
    'SECTION D ENSEIGNEMENT PROFESSIONNEL': 5,
    'CENTRE D INFORMATION ET D ORIENTATION': 6,
    'SECTION ENSEIGT GEN. ET PROF. ADAPTE': 7,
    'LYCEE ENS GENERAL TECHNO PROF AGRICOLE': 8,
    'CIRCONSCRIPTIONS INSPECTION EDUC NAT': 9,
    'ECOLE DE NIVEAU ELEMENTAIRE': 10,
    'ECOLE MATERNELLE': 11,
    'INSTITUT MEDICO-EDUCATIF': 12,
    'INSTITUT THERAPEUT. EDUCATIF PEDAGOGIQUE': 13,
    'ETAB REGIONAL/LYCEE ENSEIGNEMENT ADAPTE': 14,
    'ECOLE ELEMENTAIRE D APPLICATION': 15,
    'MAISON FAMILIALE RURALE EDUCATION ORIENT': 16,
    'SERVICE DE LA DSDEN': 17,
    'ETABLISSEMENT POUR POLY-HANDICAPES': 18,
    'DIRECTION SERVICES DEPARTEMENTAUX EN': 19,
    'ECOLE MATERNELLE D APPLICATION': 20,
    'LYCEE EXPERIMENTAL': 21,
    'COLLEGE EXPERIMENTAL': 22,
    'IES POUR DEFICIENTS VISUELS': 23,
    'LYCEE D ENSEIGNEMENT TECHNOLOGIQUE': 24,
    'INSTITUT EDUCATION MOTRICE (IEM)': 25,
    'SECTION ENSEIGT GENERAL ET TECHNOLOGIQUE': 26,
    'ECOLE PROFESSIONNELLE SPECIALISEE': 27,
    'ECOLE SECONDAIRE SPECIALISEE (2 D CYCLE)': 28,
    'ETABLISSEMENT MEDICO-EXPERIMENTAL': 29,
    'LYCEE CLIMATIQUE': 30,
}

STATUT_PUBLIC_PRIVE_MAPPING = {
    'Public': 0,
    'Privé': 1,
}

RESTAURATION_MAPPING = {
    # String values
    'OUI': 1,
    'NON': 0,
    'Yes': 1,
    'No': 0,
    # Numeric values (already integers)
    0: 0,
    1: 1,
    # String numeric values
    '0': 0,
    '1': 1,
}

# ======================================================
# INPUT VALIDATION AND MAPPING
# ======================================================

def validate_and_map_input(data: dict) -> dict:
    """
    Validate input data and apply lightweight mappings for form values.
    The actual preprocessing (encoding, scaling) is handled by the Space.
    
    Args:
        data: Raw form data as dictionary
        
    Returns:
        dict: Validated and mapped data ready for prediction
    """
    # Required fields that must be present
    required_fields = [
        "Nombre_classes_2024",
        "Nombre_eleves_2024",
        "Type_etablissement",
        "libelle_nature",
        "Statut_public_prive",
        "Restauration"
    ]
    
    # Check required fields
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Apply mappings for categorical fields
    mapped_data = data.copy()
    
    # Convert numeric strings to integers for numeric fields
    try:
        mapped_data['Nombre_classes_2024'] = int(data['Nombre_classes_2024'])
        mapped_data['Nombre_eleves_2024'] = int(data['Nombre_eleves_2024'])
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid numeric values: {str(e)}")
    
    # Type_etablissement mapping (accept both string keys and integer indices)
    type_val = data.get('Type_etablissement')
    try:
        if isinstance(type_val, (int, float)):
            mapped_data['Type_etablissement'] = int(type_val)
        elif type_val in TYPE_ETABLISSEMENT_MAPPING:
            mapped_data['Type_etablissement'] = TYPE_ETABLISSEMENT_MAPPING[type_val]
        else:
            raise ValueError(f"Invalid Type_etablissement: {type_val}")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Type_etablissement: {type_val}")
    
    # libelle_nature mapping (accept both string keys and integer indices)
    nature_val = data.get('libelle_nature')
    try:
        if isinstance(nature_val, (int, float)):
            mapped_data['libelle_nature'] = int(nature_val)
        elif nature_val in LIBELLE_NATURE_MAPPING:
            mapped_data['libelle_nature'] = LIBELLE_NATURE_MAPPING[nature_val]
        else:
            raise ValueError(f"Invalid libelle_nature: {nature_val}")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid libelle_nature: {nature_val}")
    
    # Statut_public_prive mapping (accept both string keys and integer indices)
    statut_val = data.get('Statut_public_prive')
    try:
        if isinstance(statut_val, (int, float)):
            mapped_data['Statut_public_prive'] = int(statut_val)
        elif statut_val in STATUT_PUBLIC_PRIVE_MAPPING:
            mapped_data['Statut_public_prive'] = STATUT_PUBLIC_PRIVE_MAPPING[statut_val]
        else:
            raise ValueError(f"Invalid Statut_public_prive: {statut_val}")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Statut_public_prive: {statut_val}")
    
    # Restauration mapping (accept both string keys and integer indices)
    rest_val = data.get('Restauration')
    try:
        if isinstance(rest_val, (int, float)):
            mapped_data['Restauration'] = int(rest_val)
        elif rest_val in RESTAURATION_MAPPING:
            mapped_data['Restauration'] = RESTAURATION_MAPPING[rest_val]
        else:
            raise ValueError(f"Invalid Restauration: {rest_val}")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Restauration: {rest_val}")

    return mapped_data

# ======================================================
# PREDICTION FUNCTIONS
# ======================================================
def predict_ulis_demand(data: dict):
    """
    Predict future demand for ULIS programs using KNN model.
    
    Args:
        data: Raw form data as dictionary
        
    Returns:
        dict: Prediction response including predicted demand class and confidence scores
    """
    try:
        # Check if model is loaded
        if not MODEL_LOADED or KNN_MODEL is None:
            logger.error("KNN model not loaded")
            return {"error": "Prediction model not available. Please contact administrator."}
        
        # Validate and map input
        validated_data = validate_and_map_input(data)
        
        # Prepare features for prediction
        # Expected feature order: Nombre_classes_2024, Nombre_eleves_2024, Type_etablissement, 
        #                         libelle_nature, Statut_public_prive, Restauration
        features = np.array([
            validated_data.get('Nombre_classes_2024', 0),
            validated_data.get('Nombre_eleves_2024', 0),
            validated_data.get('Type_etablissement', 0),
            validated_data.get('libelle_nature', 0),
            validated_data.get('Statut_public_prive', 0),
            validated_data.get('Restauration', 0)
        ]).reshape(1, -1)
        
        # Make prediction
        prediction = KNN_MODEL.predict(features)[0]
        
        # Get prediction probabilities if available
        try:
            probabilities = KNN_MODEL.predict_proba(features)[0]
            confidence = float(max(probabilities) * 100)
        except:
            confidence = 85.0  # Default confidence if proba not available
        
        # Map prediction to label
        prediction_labels = {
            0: "Low Demand",
            1: "Medium Demand",
            2: "High Demand"
        }
        
        prediction_label = prediction_labels.get(int(prediction), "Unknown")
        
        logger.info(f"ULIS prediction successful: {prediction_label} (confidence: {confidence:.1f}%)")
        
        return {
            "prediction": prediction_label,
            "prediction_code": int(prediction),
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

    except ValueError as e:
        logger.error(f"Validation error in predict_ulis_demand: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in predict_ulis_demand: {e}")
        return {"error": "Prediction failed. Please check your input data."}
 
