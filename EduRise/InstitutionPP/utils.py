import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def predict_cluster(nombre_classes, eleves_premier, eleves_superieur, latitude, longitude):
    """
    Predict cluster for a new institution using HuggingFace API.
    
    Args:
        nombre_classes: Number of classes (2009)
        eleves_premier: Number of primary students
        eleves_superieur: Number of secondary students
        latitude: Geographic latitude
        longitude: Geographic longitude
    
    Returns:
        int: Predicted cluster (0-3)
    """
    try:
        url = f"{settings.HUGGINGFACE_API_URL}/predict/cluster"
        
        payload = {
            "nombre_classes_2009": float(nombre_classes),
            "eleves_premier": float(eleves_premier),
            "eleves_superieur": float(eleves_superieur),
            "latitude": float(latitude),
            "longitude": float(longitude)
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return int(result['cluster'])
        
    except requests.RequestException as e:
        logger.error(f"HuggingFace API error: {e}")
        raise Exception(f"Failed to predict cluster: {str(e)}")


def predict_public_private(form_data):
    """
    Predict if an institution is public (0) or private (1) using HuggingFace API.
    
    Args:
        form_data: Dictionary with 8 features
                  Must include: nombre_classes_2009, eleves_premier, eleves_superieur,
                               latitude, longitude, restauration, hebergement, ulis
    
    Returns:
        tuple: (prediction, probability)
            prediction (int): 0 for Public, 1 for Private
            probability (float): Confidence percentage (0-100)
    """
    try:
        url = f"{settings.HUGGINGFACE_API_URL}/predict/public-private"
        
        # Prepare payload with only the 8 features the model was trained on
        payload = {
            "nombre_classes_2009": float(form_data['nombre_classes_2009']),
            "eleves_premier": float(form_data['eleves_premier']),
            "eleves_superieur": float(form_data['eleves_superieur']),
            "latitude": float(form_data['latitude']),
            "longitude": float(form_data['longitude']),
            "restauration": int(form_data['restauration']),
            "hebergement": int(form_data['hebergement']),
            "ulis": int(form_data['ulis'])
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return int(result['prediction']), result['probability'] * 100
        
    except requests.RequestException as e:
        logger.error(f"HuggingFace API error: {e}")
        raise Exception(f"Failed to predict public/private: {str(e)}")
 
