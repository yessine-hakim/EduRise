"""
ML Service Client for communicating with Hugging Face Spaces.
"""

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class MLServiceClient:
    """
    Client for the external ML FastAPI service.
    """
    
    def __init__(self):
        self.api_url = settings.HF_SPACE_URL.rstrip('/')
        self.FEATURE_ORDER = [
            "Code_departement",
            "Nombre_Eleves_Totale",
            "Type_etablissement",
            "Statut_public_prive",
            "libelle_nature",
            "latitude",
            "Code_region",
            "ULIS",
            "Eleves_per_class_last",
        ]
        
    def predict(self, features: dict, model_type: str) -> dict:
        """
        Send prediction request to the external service.
        """
        url = f"{self.api_url}/predict"
        
        payload = {
            "model_type": model_type,
            "features": features
        }
        
        try:
            logger.info(f"Sending prediction request to {url} for {model_type}")
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"ML API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"API Response: {e.response.text}")
            raise Exception("ML Service Unavailable")

# Singleton instance
_client = None

def get_ml_client():
    global _client
    if _client is None:
        _client = MLServiceClient()
    return _client
 
