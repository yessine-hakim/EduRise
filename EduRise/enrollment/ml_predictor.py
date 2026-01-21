import os
import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ======================================================
# HUGGING FACE SPACE CONFIG
# ======================================================
HF_SPACE_URL = "https://nefissi12-edurise.hf.space"  # Update with your actual space URL
PREDICT_ENDPOINT = f"{HF_SPACE_URL}/predict"
REQUEST_TIMEOUT = 30  # seconds

# ======================================================
# MAPPINGS FOR FORM VALUES TO INTEGERS
# ======================================================
TYPE_MAPPING = {
    'Lycée': 0,
    'Collège': 1,
    'Information et orientation': 2,
    'Autre': 3,
    'École': 4,
    'Médico-social': 5,
    'EREA': 6,
}

STATUT_MAPPING = {
    'Public': 0,
    'Privé': 1,
}

NATURE_CHOICES = [
    'LYCEE PROFESSIONNEL',
    'COLLEGE',
    'LYCEE POLYVALENT',
    'LYCEE D ENSEIGNEMENT GENERAL',
    'LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE',
    'SECTION D ENSEIGNEMENT PROFESSIONNEL',
    'CENTRE D INFORMATION ET D ORIENTATION',
    'SECTION ENSEIGT GEN. ET PROF. ADAPTE',
    'LYCEE ENS GENERAL TECHNO PROF AGRICOLE',
    'CIRCONSCRIPTIONS INSPECTION EDUC NAT',
    'ECOLE DE NIVEAU ELEMENTAIRE',
    'ECOLE MATERNELLE',
    'INSTITUT MEDICO-EDUCATIF',
    'INSTITUT THERAPEUT. EDUCATIF PEDAGOGIQUE',
    'ETAB REGIONAL/LYCEE ENSEIGNEMENT ADAPTE',
    'ECOLE ELEMENTAIRE D APPLICATION',
    'MAISON FAMILIALE RURALE EDUCATION ORIENT',
    'SERVICE DE LA DSDEN',
    'ETABLISSEMENT POUR POLY-HANDICAPES',
    'DIRECTION SERVICES DEPARTEMENTAUX EN',
    'ECOLE MATERNELLE D APPLICATION',
    'LYCEE EXPERIMENTAL',
    'COLLEGE EXPERIMENTAL',
    'IES POUR DEFICIENTS VISUELS',
    'LYCEE D ENSEIGNEMENT TECHNOLOGIQUE',
    'INSTITUT EDUCATION MOTRICE (IEM)',
    'SECTION ENSEIGT GENERAL ET TECHNOLOGIQUE',
    'ECOLE PROFESSIONNELLE SPECIALISEE',
    'ECOLE SECONDAIRE SPECIALISEE (2 D CYCLE)',
    'ETABLISSEMENT MEDICO-EXPERIMENTAL',
    'LYCEE CLIMATIQUE',
    'LYCEE ENS GENERAL TECHNO PROF AGRICOLE',
    'LYCEE EXPERIMENTAL',  # duplicate, but keep
]

NATURE_MAPPING = {choice: idx for idx, choice in enumerate(NATURE_CHOICES)}

HEBERGEMENT_MAPPING = {
    0: 0,
    1: 1,
    '0': 0,
    '1': 1,
}

RESTAURATION_MAPPING = {
    0: 0,
    1: 1,
    '0': 0,
    '1': 1,
}

ULIS_MAPPING = {
    0: 0,
    1: 1,
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
    """
    # Default values for optional fields
    defaults = {
        'latitude': 48.8566,  # Paris coordinates as default
        'longitude': 2.3522,  # Paris coordinates as default
        'Restauration': 0,    # No catering by default
        'ULIS': 0,            # No ULIS by default
    }
    
    # Apply defaults for missing or empty optional fields
    processed_data = data.copy()
    for field, default_value in defaults.items():
        if field not in processed_data or processed_data[field] is None or processed_data[field] == '':
            processed_data[field] = default_value
    
    # Required fields that must be present
    required_fields = [
        "Type_etablissement", "Statut_public_prive", "libelle_nature", "Hebergement",
        "Nombre_classes_2023", "Eleves_Superieur"
    ]
    
    # Check required fields
    missing_fields = []
    for field in required_fields:
        if field not in processed_data or processed_data[field] is None or processed_data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Apply mappings for categorical fields (optional, for consistency)
    mapped_data = processed_data.copy()
    
    # Type_etablissement mapping
    if data.get('Type_etablissement') in TYPE_MAPPING:
        mapped_data['Type_etablissement'] = TYPE_MAPPING[data['Type_etablissement']]
    
    # Statut_public_prive mapping
    if data.get('Statut_public_prive') in STATUT_MAPPING:
        mapped_data['Statut_public_prive'] = STATUT_MAPPING[data['Statut_public_prive']]

    # libelle_nature mapping
    if data.get('libelle_nature') in NATURE_MAPPING:
        mapped_data['libelle_nature'] = NATURE_MAPPING[data['libelle_nature']]

    # Boolean mappings
    mapped_data['Hebergement'] = HEBERGEMENT_MAPPING.get(mapped_data.get('Hebergement'), mapped_data.get('Hebergement'))
    mapped_data['Restauration'] = RESTAURATION_MAPPING.get(mapped_data.get('Restauration'), mapped_data.get('Restauration'))
    mapped_data['ULIS'] = ULIS_MAPPING.get(mapped_data.get('ULIS'), mapped_data.get('ULIS'))

    return mapped_data

# ======================================================
# HTTP CLIENT FOR PREDICTIONS
# ======================================================
def send_prediction_request(data: dict, model_type: str):
    """
    Send prediction request to Hugging Face Space.

    Args:
        data: Input features as dict
        model_type: Type of model ('growth' or 'cluster')

    Returns:
        dict: Prediction response from the Space
    """
    payload = {
        "model_type": model_type,
        "features": data
    }

    try:
        response = requests.post(
            PREDICT_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 404:
            logger.error(f"Endpoint {PREDICT_ENDPOINT} not found. Make sure your FastAPI app is deployed to the Hugging Face Space.")
            return {"error": "Prediction endpoint not found. Please check if your FastAPI application is properly deployed to the Hugging Face Space."}
        elif response.status_code == 500:
            logger.error(f"Server error from {PREDICT_ENDPOINT}: {response.text}")
            return {"error": "Prediction service internal error. Please check your model deployment."}
        elif response.status_code >= 400:
            logger.error(f"Client error {response.status_code} from {PREDICT_ENDPOINT}: {response.text}")
            return {"error": f"Prediction service error ({response.status_code}). Please check your request format."}

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error calling {PREDICT_ENDPOINT}")
        return {"error": "Request timeout - the prediction service may be overloaded. Please try again."}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error calling {PREDICT_ENDPOINT}")
        return {"error": "Cannot connect to prediction service. Please check your internet connection."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error calling {PREDICT_ENDPOINT}: {e}")
        return {"error": f"Service unavailable: {str(e)}"}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from {PREDICT_ENDPOINT}: {e}")
        return {"error": "Invalid response format from prediction service."}

# ======================================================
# PREDICTION FUNCTIONS
# ======================================================
def predict_growth_class(data: dict):
    """
    Predict school growth class using Hugging Face Space.
    """
    try:
        validated_data = validate_and_map_input(data)
        response = send_prediction_request(validated_data, "growth")

        if "error" in response:
            return response

        # Ensure response has expected structure
        if not all(key in response for key in ['class', 'class_label']):
            return {"error": "Invalid response structure from prediction service"}

        return response

    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in predict_growth_class: {e}")
        return {"error": "Prediction service unavailable"}

def predict_cluster(data: dict):
    """
    Predict school cluster using Hugging Face Space.
    """
    try:
        validated_data = validate_and_map_input(data)
        response = send_prediction_request(validated_data, "cluster")

        if "error" in response:
            # Return default on error
            return {"cluster": 0, "cluster_label": "Small institutions / rural areas"}

        # Ensure response has expected structure
        if not all(key in response for key in ['cluster', 'cluster_label']):
            return {"cluster": 0, "cluster_label": "Small institutions / rural areas"}

        return response

    except Exception as e:
        logger.error(f"Error in predict_cluster: {e}")
        # Return default cluster on error
        return {"cluster": 0, "cluster_label": "Small institutions / rural areas"} 
