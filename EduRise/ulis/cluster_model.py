import os
import joblib
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def get_department_clusters(data_dir):
    """
    Load department data and KMeans model, return list of clusters with stats.
    
    Args:
        data_dir (str): Path to the directory containing data files
        
    Returns:
        tuple: (list_of_dicts, error_message_or_None)
        
    Each dict in list contains: 
    { 
        'cluster_id': int, 
        'count': int, 
        'avg_inclusif_prop': float, 
        'departments': list_of_codes 
    }
    """
    try:
        csv_path = os.path.join(data_dir, 'departements_analyse_clusters.csv')
        # Model is expected to be in the models subdirectory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'models', 'cluster_model.joblib')
        
        # Fallback to current directory if not found in models
        if not os.path.exists(model_path):
             model_path = os.path.join(current_dir, 'cluster_model.joblib')

        if not os.path.exists(csv_path):
            return None, f"Data file not found: {csv_path}"
        
        # If model missing, we will proceed to fit a new one (handled below), 
        # so don't return error here immediately unless strictly necessary.
        # But for now, let's keep the check but soft it if we want auto-fit.
        # However, the previous logic returned error. Let's rely on the try-except block later.
        # if not os.path.exists(model_path):
        #    return None, f"Model file not found: {model_path}"

        df = pd.read_csv(csv_path)
        
        # Calculate Prop_Inclusifs if not present (likely needed for prioritization logic)
        # Assuming Prop_Inclusifs = Nb_Inclusifs / Total_Etablissements
        if 'Prop_Inclusifs' not in df.columns:
            if 'Nb_Inclusifs' in df.columns and 'Total_Etablissements' in df.columns:
                df['Prop_Inclusifs'] = df.apply(
                    lambda row: row['Nb_Inclusifs'] / row['Total_Etablissements'] 
                    if row['Total_Etablissements'] and row['Total_Etablissements'] > 0 else 0.0, 
                    axis=1
                )
            else:
                # If we cannot calculate it, initialize to 0
                df['Prop_Inclusifs'] = 0.0

        # Prepare features for prediction
        # We attempt to use the standardized/score columns that are typical for such clustering
        feature_cols = [
            'Prop_Surchargés', 'Prop_Basiques', 
            'Moy_Eleves', 'Ratio_Eleves_Etab', 
            'Score_OverEquipped', 'Score_UnderEquipped'
        ]
        
        # Verify columns exist
        missing_cols = [c for c in feature_cols if c not in df.columns]
        if missing_cols:
             return None, f"Missing feature columns for clustering: {missing_cols}"
             
        X = df[feature_cols].fillna(0)

        # Load model and predict
        model = joblib.load(model_path)
        
        # Basic validation of feature count
        if hasattr(model, 'n_features_in_') and model.n_features_in_ != X.shape[1]:
             # If feature count mismatch, we might want to re-fit a new model or warn
             # For robustness, we'll try to use it, but if it fails, we fall back to fitting
             pass

        try:
            labels = model.predict(X)
        except Exception:
            # If model is not fitted or other error (e.g. feature mismatch), fit it now
            # logger.warning("Model not fitted or incompatible. Fitting on current data.")
            try:
                # Ensure we have a valid KMeans object
                if not hasattr(model, 'fit'):
                     from sklearn.cluster import KMeans
                     model = KMeans(n_clusters=4, random_state=42)
                
                model.fit(X)
                labels = model.predict(X)
            except Exception as e:
                return None, f"Failed to fit/predict clusters: {e}"

        df['cluster'] = labels

        # Aggregate results
        clusters = []
        unique_clusters = sorted(df['cluster'].unique())
        
        for cid in unique_clusters:
            cluster_df = df[df['cluster'] == cid]
            
            avg_incl = 0.0
            if 'Prop_Inclusifs' in cluster_df.columns:
                avg_incl = cluster_df['Prop_Inclusifs'].mean()
            
            clusters.append({
                'cluster_id': int(cid),
                'count': int(len(cluster_df)),
                'avg_inclusif_prop': float(avg_incl),
                'departments': cluster_df['Code_departement'].astype(str).tolist()
            })

        return clusters, None

    except Exception as e:
        logger.error(f"Error in get_department_clusters: {e}")
        return None, str(e)
 
