"""
ML Loader for Institutions Predictions

This module handles loading the Random Forest student prediction model
via the Hugging Face Space API.
"""

import requests
import joblib
import logging
import json
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

# ======================================================
# HUGGING FACE CONFIG
# ======================================================
HF_SPACE_URL = "https://yessinehakim-extramodels.hf.space"
PREDICT_ENDPOINT = f"{HF_SPACE_URL}/predict"
FEATURES_ENDPOINT = f"{HF_SPACE_URL}/features"
REQUEST_TIMEOUT = 30  # seconds

# Default features fallback if API fails (matches views.py default)
DEFAULT_FEATURES = [
    'Nombre_classes_2024', 'Code_departement', 'Type_etablissement', 
    'Statut_public_prive', 'latitude', 'longitude', 
    'Restauration', 'Hebergement', 'ULIS'
]

# ======================================================
# CLIENT FOR REMOTE API
# ======================================================

class RemoteModelClient:
    """
    Client for the remote Model API on Hugging Face.
    """
    def __init__(self):
        self.endpoint = PREDICT_ENDPOINT
        self.features_endpoint = FEATURES_ENDPOINT
        self.feature_order = self._fetch_feature_order()

    def _fetch_feature_order(self):
        try:
            response = requests.get(self.features_endpoint, timeout=10)
            if response.status_code == 200:
                features = response.json().get("features", [])
                if features:
                    logger.info("✅ Fetched feature order from remote API")
                    return features
        except Exception as e:
            logger.warning(f"Failed to fetch features from API: {e}")
        
        logger.info("⚠️ Using default feature order fallback")
        return list(DEFAULT_FEATURES)

    def predict(self, features: dict):
        """
        Send prediction request to the remote API.
        """
        payload = {"features": features}
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Error from prediction API: {response.status_code} - {response.text}")
                return None
                
            result = response.json()
            return result.get("prediction")
            
        except Exception as e:
            logger.error(f"Failed to call prediction API: {e}")
            return None

# ======================================================
# ADAPTER FOR EXISTING CODE
# ======================================================

class ModelAdapter:
    """
    A class that mimics the sklearn model interface but calls the remote API.
    Used to minimize changes in views.py.
    """
    def __init__(self):
        self.client = RemoteModelClient()
        self.feature_names_in_ = self.client.feature_order

    def predict(self, X):
        """
        X: pandas DataFrame, dict, list, or numpy array
        """
        predictions = []
        
        # Helper to process a single record
        def process_record(record):
            # If record is a numpy array (row), need to map to dict using keys
            if isinstance(record, (np.ndarray, list)):
                if not self.feature_names_in_:
                    logger.error("Cannot map array input to features: feature names unknown")
                    return 0
                # Zip names with values. Handle length mismatch gracefully
                features_dict = {}
                for i, key in enumerate(self.feature_names_in_):
                    if i < len(record):
                        features_dict[key] = record[i]
                    else:
                        features_dict[key] = 0 # Default if short
                return self.client.predict(features_dict)
            else:
                # Assume dict-like
                return self.client.predict(record)


        # Handle input types
        if hasattr(X, 'to_dict'):
            # DataFrame
            records = X.to_dict(orient='records')
            for record in records:
                pred = process_record(record)
                predictions.append(pred if pred is not None else 0)
                
        elif isinstance(X, np.ndarray):
            # Numpy array
            if X.ndim == 1:
                # 1D array - single sample
                pred = process_record(X)
                predictions.append(pred if pred is not None else 0)
            else:
                # 2D array - list of samples
                for row in X:
                    pred = process_record(row)
                    predictions.append(pred if pred is not None else 0)
                    
        elif isinstance(X, list):
             # List of records or list of values
             # Heuristic: if first item is list/dict, treat as list of samples
             if len(X) > 0 and isinstance(X[0], (list, dict, np.ndarray)):
                 for item in X:
                     pred = process_record(item)
                     predictions.append(pred if pred is not None else 0)
             else:
                 # treat as single sample vector
                 pred = process_record(X)
                 predictions.append(pred if pred is not None else 0)
                 
        elif isinstance(X, dict):
             pred = process_record(X)
             predictions.append(pred if pred is not None else 0)
        
        else:
             logger.error(f"Unsupported input type for prediction: {type(X)}")
             return np.array([0])

        return np.array(predictions)

def load_student_prediction_model():
    """
    Returns (model_adapter, feature_order) tuple.
    """
    model = ModelAdapter()
    feature_order = model.feature_names_in_
    
    logger.info("✅ Remote Model Adapter initialized")
    return model, feature_order

# Singleton instance
_model = None
_features = None
_loaded = False

def get_prediction_model():
    """
    Get the singleton instance of the student prediction model.
    Returns (model, feature_order) tuple.
    """
    global _model, _features, _loaded
    
    if not _loaded:
        _model, _features = load_student_prediction_model()
        _loaded = True
    
    return _model, _features
 
