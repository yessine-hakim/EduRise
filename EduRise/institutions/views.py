import os
import csv
import json
import logging
import joblib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.utils.safestring import mark_safe
from .forms import InstitutionsPredictionForm
from .ml_loader import get_prediction_model

logger = logging.getLogger(__name__)


def is_institution_admin_or_manager(user):
    return user.is_authenticated and (user.is_admin() or user.is_institution_manager())


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _load_priority_departments(data_dir):
    """Top départements surchargés (rapport PowerBI)."""
    path = os.path.join(data_dir, 'rapport_powerbi_departements_complet.csv')
    results = []
    try:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                surcharge_pct = _safe_float(row.get('Proportion_Surcharges_Pct'))
                results.append({
                    'departement': row.get('Nom_Departement', 'N/A'),
                    'surcharge_pct': surcharge_pct,
                    'danger': row.get('Danger_Level_GLOBAL', ''),
                    'action': row.get('Recommandation_Action', ''),
                    'total_etab': row.get('Total_Etablissements', ''),
                    'taux_restauration': row.get('Taux_Restauration_Pct', ''),
                    'taux_hebergement': row.get('Taux_Hebergement_Pct', ''),
                })
        results = sorted(results, key=lambda r: r['surcharge_pct'], reverse=True)[:6]
    except Exception as e:
        logger.error(f"Failed to load priority departments: {e}")
    return results


def _load_new_institution_departments(data_dir):
    """Départements nécessitant de nouvelles institutions (cluster)."""
    path = os.path.join(data_dir, 'recommandations_departements_nouvelles_institutions.csv')
    items = []
    try:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append({
                    'departement': row.get('Nom_Departement', 'N/A'),
                    'nb_surcharges': int(_safe_float(row.get('Nb_Etablissements_Surcharges'))),
                    'eleves': int(_safe_float(row.get('Total_Eleves'))),
                    'score': _safe_float(row.get('Score_Besoin')),
                    'distance': _safe_float(row.get('Distance_Moyenne_km')),
                    'eleves_par_etab': _safe_float(row.get('Eleves_Moyen_Par_Etab')),
                })
        items = sorted(items, key=lambda r: r['score'], reverse=True)[:8]
    except Exception as e:
        logger.error(f"Failed to load department recommendations: {e}")
    return items


def _load_priority_zones(data_dir):
    """Zones géolocalisées pour nouvelles institutions (top score)."""
    path = os.path.join(data_dir, 'recommandations_nouvelles_institutions.csv')
    zones = []
    try:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                zones.append({
                    'zone_id': row.get('Zone_ID'),
                    'departement': row.get('Departement'),
                    'type': row.get('Type_Recommande'),
                    'score': _safe_float(row.get('Score_Priorite')),
                    'eleves': int(_safe_float(row.get('Total_Eleves'))),
                    'classes': int(_safe_float(row.get('Total_Classes'))),
                    'lat': row.get('Latitude'),
                    'lng': row.get('Longitude'),
                })
        zones = sorted(zones, key=lambda r: r['score'], reverse=True)[:8]
    except Exception as e:
        logger.error(f"Failed to load priority zones: {e}")
    return zones


def _load_optimal_zones(data_dir):
    """Sites optimaux de construction."""
    path = os.path.join(data_dir, 'zones_optimales_construction.csv')
    rows = []
    try:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({
                    'departement': row.get('Nom_Departement', 'N/A'),
                    'nb_etab': int(_safe_float(row.get('Nb_Etablissements'))),
                    'eleves': int(_safe_float(row.get('Total_Eleves'))),
                    'lat': row.get('Latitude_Optimale'),
                    'lng': row.get('Longitude_Optimale'),
                    'priorite': row.get('Priorite', ''),
                })
        # Keep top 6, prioritizing ÉLEVÉE then the rest
        rows = sorted(rows, key=lambda r: (r['priorite'] != 'ÉLEVÉE', -r['nb_etab']))[:6]
    except Exception as e:
        logger.error(f"Failed to load optimal zones: {e}")
    return rows


def _load_cluster_dataset(data_path):
    """Load proportions per cluster without pandas/plotly server deps."""
    if not os.path.exists(data_path):
        return None, "Fichier departements_analyse_clusters.csv introuvable."

    required = ['Code_departement', 'Total_Etablissements', 'Nb_Inclusifs', 'Nb_Standard', 'Nb_Basiques', 'Nb_Surchargés']
    rows = []
    try:
        with open(data_path, encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            missing = [c for c in required if c not in reader.fieldnames]
            if missing:
                return None, f"Colonnes manquantes : {', '.join(missing)}"

            for row in reader:
                total = _safe_float(row.get('Total_Etablissements'), 0.0)
                if total <= 0:
                    continue
                code = str(row.get('Code_departement', '')).strip().zfill(2)
                rows.append({
                    'code': code,
                    'c0': _safe_float(row.get('Nb_Inclusifs'), 0.0) / total,
                    'c1': _safe_float(row.get('Nb_Standard'), 0.0) / total,
                    'c2': _safe_float(row.get('Nb_Basiques'), 0.0) / total,
                    'c3': _safe_float(row.get('Nb_Surchargés'), 0.0) / total,
                })
    except Exception as exc:  # pragma: no cover
        logger.error("Erreur lecture cluster dataset: %s", exc)
        return None, str(exc)

    return rows, None


def _load_department_metrics(data_dir):
    """Merge département metrics for search (names + totals + surcharges)."""
    rapport_path = os.path.join(data_dir, 'rapport_powerbi_departements_complet.csv')
    clusters_path = os.path.join(data_dir, 'departements_analyse_clusters.csv')

    by_code = {}
    surcharges_by_code = {}

    try:
        with open(rapport_path, encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                code = str(row.get('Code_Departement', '')).strip()
                if not code:
                    continue
                by_code[code] = {
                    'code': code,
                    'name': row.get('Nom_Departement', 'N/A'),
                    'total_etab': int(_safe_float(row.get('Total_Etablissements'))),
                }
    except Exception as e:
        logger.error(f"Failed to load rapport_powerbi_departements_complet.csv: {e}")

    try:
        with open(clusters_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = str(row.get('Code_departement', '')).strip()
                if not code:
                    continue
                surcharges_by_code[code] = int(_safe_float(row.get('Nb_Surchargés')))
    except Exception as e:
        logger.error(f"Failed to load departements_analyse_clusters.csv: {e}")

    merged = []
    for code, data in by_code.items():
        merged.append({
            'code': code,
            'name': data.get('name'),
            'total_etab': data.get('total_etab', 0),
            'nb_surcharges': surcharges_by_code.get(code, 0),
        })

    return sorted(merged, key=lambda r: r['name'])


@login_required
@user_passes_test(is_institution_admin_or_manager)
def recommendations(request):
    data_dir = os.path.join(settings.BASE_DIR, 'data')

    priority_departments = _load_priority_departments(data_dir)
    new_institution_departments = _load_new_institution_departments(data_dir)
    optimal_zones = _load_optimal_zones(data_dir)
    departments_metrics = _load_department_metrics(data_dir)

    map_cards = [
        {"title": "Vue globale", "file": "maps/carte_vue_globale.html", "desc": "Lecture complète du territoire pour situer les besoins."},
        {"title": "Top 50 surcharges", "file": "maps/carte_top50_surcharges.html", "desc": "Hotspots avec surcharge élève/classe."},
        {"title": "Tous les surcharges", "file": "maps/carte_tous_surcharges.html", "desc": "Distribution de toutes les zones en tension."},
        {"title": "Heatmap besoins", "file": "maps/carte_heatmap.html", "desc": "Chaleur de la demande à l'échelle nationale."},
        {"title": "Carte prédictive", "file": "maps/recommandations_carte_complete.html", "desc": "Localisation prédite des futures institutions."},
    ]

    context = {
        'map_cards': map_cards,
        'priority_departments': priority_departments,
        'new_institution_departments': new_institution_departments,
        'optimal_zones': optimal_zones,
        'departments_metrics': departments_metrics,
        'predict_map_path': 'maps/recommandations_carte_complete.html',
    }

    return render(request, 'institutions/institutions.html', context)


@login_required
@user_passes_test(is_institution_admin_or_manager)
def clusters_overview(request):
    """Static narrative + Plotly grid showing cluster dominance by département."""
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    data_path = os.path.join(data_dir, 'departements_analyse_clusters.csv')

    cluster_cards = [
        {
            'id': 0,
            'title': 'Cluster 0 : Établissements inclusifs',
            'share': '18.7% · 12 137 établissements',
            'bullets': [
                'Ratio élèves/classe : 1.0 (faible densité)',
                'Charge d’élèves moyenne ou légèrement basse (-0.058)',
                'Un peu moins publics que les autres groupes',
            ],
            'actions': [
                'Forte capacité d’accueil pour élèves à besoins spécifiques',
                'Infrastructures adaptées (ULIS)',
                'Densité modérée permettant un accompagnement personnalisé',
            ],
        },
        {
            'id': 1,
            'title': 'Cluster 1 : Établissements standard',
            'share': '31.1% · 20 159 établissements',
            'bullets': [
                'Ratio élèves/classe : 1.2 (densité légèrement élevée)',
                'Services potentiellement bons',
            ],
            'actions': [
                'Équilibrés avec services complets',
                'Profil “classique” du système éducatif français',
            ],
        },
        {
            'id': 2,
            'title': 'Cluster 2 : Petits établissements basiques',
            'share': '40.8% · 26 438 établissements',
            'bullets': [
                'Ratio élèves/classe : 1.1 (densité normale)',
                'Infrastructure minimale, peu de services additionnels',
                'Manque d’équipements spécialisés (ULIS, hébergement)',
            ],
            'actions': [
                'Zones prioritaires pour amélioration des infrastructures',
            ],
        },
        {
            'id': 3,
            'title': 'Cluster 3 : Établissements surchargés',
            'share': '9.3% · 6 021 établissements',
            'bullets': [
                'Nombre de classes : 2.01',
                'Nombre d’élèves : 2 (le plus élevé)',
            ],
            'actions': [
                'Établissements en situation de surcharge',
            ],
        },
    ]

    priority_table = [
        {'cluster': 0, 'profil': 'Inclusifs', 'effectifs': '18.7%', 'priorite': 'Modèle', 'action': 'Maintenir et reproduire'},
        {'cluster': 1, 'profil': 'Standard', 'effectifs': '31.1%', 'priorite': 'Stable', 'action': 'Monitoring régulier'},
        {'cluster': 2, 'profil': 'Basiques', 'effectifs': '40.8%', 'priorite': 'Élevée', 'action': 'Améliorer équipements'},
        {'cluster': 3, 'profil': 'Surchargés', 'effectifs': '9.3%', 'priorite': 'Critique', 'action': 'Construction immédiate'},
    ]

    cluster_map_data, map_error = _load_cluster_dataset(data_path)

    context = {
        'cluster_cards': cluster_cards,
        'priority_table': priority_table,
        'map_error': map_error,
    }

    # JSON helpers for front-end interactions (detail + map)
    context['cluster_cards_json'] = json.dumps(cluster_cards)

    if cluster_map_data:
        context['cluster_map_json'] = json.dumps(cluster_map_data)

    return render(request, 'institutions/clusters.html', context)


def _find_model_paths():
    """Yield candidate paths for model and feature files."""
    base = settings.BASE_DIR
    candidates = [
        os.path.join(base, 'rfr_student_model.joblib'),
        os.path.join(base, 'models', 'rfr_student_model.joblib'),
        os.path.join(base, 'services', 'rfr_student_model.joblib'),
        os.path.join(base, 'val ML', 'rfr_student_model.joblib'),
    ]
    return candidates


def _find_features_paths():
    base = settings.BASE_DIR
    candidates = [
        os.path.join(base, 'model_features.joblib'),
        os.path.join(base, 'models', 'model_features.joblib'),
        os.path.join(base, 'services', 'model_features.joblib'),
        os.path.join(base, 'val ML', 'model_features.joblib'),
    ]
    return candidates


def _load_model():
    """Try to load a joblib model and return (model, feature_order) or (None, None) if not found."""
    model = None
    features = None

    for p in _find_model_paths():
        try:
            if os.path.exists(p):
                model = joblib.load(p)
                logger.info(f"Loaded model from {p}")
                break
        except Exception as e:
            logger.error(f"Failed to load model from {p}: {e}")

    if model:
        for fp in _find_features_paths():
            try:
                if os.path.exists(fp):
                    features = joblib.load(fp)
                    logger.info(f"Loaded feature order from {fp}")
                    break
            except Exception as e:
                logger.error(f"Failed to load feature order from {fp}: {e}")

    return model, features


def _find_scaler_X_paths():
    base = settings.BASE_DIR
    candidates = [
        os.path.join(base, 'scaler_X.joblib'),
        os.path.join(base, 'models', 'scaler_X.joblib'),
        # backward-compatible fallbacks
        os.path.join(base, 'scaler.joblib'),
        os.path.join(base, 'models', 'scaler.joblib'),
    ]
    return candidates


def _find_scaler_X_features_paths():
    base = settings.BASE_DIR
    candidates = [
        os.path.join(base, 'scaler_X_features.joblib'),
        os.path.join(base, 'models', 'scaler_X_features.joblib'),
        # fallback
        os.path.join(base, 'scaler_features.joblib'),
        os.path.join(base, 'models', 'scaler_features.joblib'),
    ]
    return candidates


def _find_scaler_y_paths():
    base = settings.BASE_DIR
    candidates = [
        os.path.join(base, 'scaler_y.joblib'),
        os.path.join(base, 'models', 'scaler_y.joblib'),
    ]
    return candidates


def _load_scalers():
    scaler_X = None
    scaler_X_features = None
    scaler_y = None

    for p in _find_scaler_X_paths():
        try:
            if os.path.exists(p):
                scaler_X = joblib.load(p)
                logger.info(f"Loaded scaler_X from {p}")
                break
        except Exception as e:
            logger.error(f"Failed to load scaler_X from {p}: {e}")

    if scaler_X:
        for fp in _find_scaler_X_features_paths():
            try:
                if os.path.exists(fp):
                    scaler_X_features = joblib.load(fp)
                    logger.info(f"Loaded scaler_X features from {fp}")
                    break
            except Exception as e:
                logger.error(f"Failed to load scaler_X features from {fp}: {e}")

    for p in _find_scaler_y_paths():
        try:
            if os.path.exists(p):
                scaler_y = joblib.load(p)
                logger.info(f"Loaded scaler_y from {p}")
                break
        except Exception as e:
            logger.error(f"Failed to load scaler_y from {p}: {e}")

    return scaler_X, scaler_X_features, scaler_y


def _find_train_metadata_paths():
    base = settings.BASE_DIR
    candidates = [
        os.path.join(base, 'train_metadata.json'),
        os.path.join(base, 'models', 'train_metadata.json'),
    ]
    return candidates


def _load_train_metadata():
    for p in _find_train_metadata_paths():
        try:
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as fh:
                    return joblib.load(p) if p.endswith('.joblib') else __import__('json').load(fh)
        except Exception as e:
            logger.error(f"Failed to read train metadata from {p}: {e}")
    return None


@login_required
@user_passes_test(is_institution_admin_or_manager)
def prediction(request):
    """Predict Nombre_eleves_2024 using a trained RandomForest (if available).

    Fallback behavior: if model not found, show an error message and do not perform prediction.
    """
    form = None
    prediction_result = None

    model, feature_order = get_prediction_model()

    if request.method == 'POST':
        form = InstitutionsPredictionForm(request.POST)
        if form.is_valid():
            if model is None:
                messages.error(request, "Model not found on server. Please provide 'rfr_student_model.joblib' and 'model_features.joblib' in project root or models/ folder.")
            else:
                try:
                    # Determine expected feature order
                    expected_features = None
                    if feature_order:
                        # prefer the saved feature order provided with the model
                        expected_features = feature_order
                    elif hasattr(model, 'feature_names_in_'):
                        expected_features = list(model.feature_names_in_)
                    else:
                        # Fallback to form default order
                        expected_features = ['Nombre_classes_2024', 'Code_departement', 'Type_etablissement', 'Statut_public_prive', 'latitude', 'longitude', 'Restauration', 'Hebergement', 'ULIS']

                    # Try to get features directly from form; if form cannot provide a feature, fill with 0 and warn
                    try:
                        vec = form.get_feature_vector(feature_order=expected_features)
                        import pandas as pd
                        row = pd.DataFrame([vec], columns=expected_features)
                    except KeyError as ke:
                        # construct mapping from form's default order
                        default_order = ['Nombre_classes_2024', 'Code_departement', 'Type_etablissement', 'Statut_public_prive', 'latitude', 'longitude', 'Restauration', 'Hebergement', 'ULIS']
                        default_vec = form.get_feature_vector()
                        feature_map = dict(zip(default_order, default_vec))

                        # Build row with expected_features, filling missing ones with 0.0
                        filled = []
                        missing = []
                        for f in expected_features:
                            if f in feature_map:
                                filled.append(feature_map[f])
                            else:
                                filled.append(0.0)
                                missing.append(f)

                        import pandas as pd
                        row = pd.DataFrame([filled], columns=expected_features)

                        if missing:
                            logger.warning(f"Model expects features not provided by form: {missing}. Filling with 0s.")
                            messages.warning(request, f"Note: model expects additional features {missing}; filled with 0 which may affect predictions.")

                    # Load scalers (predictors and target)
                    scaler_X, scaler_X_features, scaler_y = _load_scalers()

                    # Determine feature list the model expects (predictor order)
                    if feature_order:
                        model_predictor_features = feature_order
                    elif hasattr(model, 'feature_names_in_'):
                        model_predictor_features = list(model.feature_names_in_)
                    else:
                        model_predictor_features = ['Nombre_classes_2024', 'Code_departement', 'Type_etablissement', 'Statut_public_prive', 'latitude', 'longitude', 'Restauration', 'Hebergement', 'ULIS']

                    # Ensure row contains all features used by scaler_X or model
                    union_features = set(model_predictor_features) | set(scaler_X_features or [])
                    for f in union_features:
                        if f not in row.columns:
                            row[f] = 0.0

                    # Build scaled input for the model
                    import numpy as _np
                    if scaler_X is not None and scaler_X_features:
                        # Ensure scaler feature columns exist
                        for sf in scaler_X_features:
                            if sf not in row.columns:
                                row[sf] = 0.0

                        scaled_vals = scaler_X.transform(row[scaler_X_features])

                        # Reorder or select scaled values to match model_predictor_features
                        scaled_for_model = _np.zeros((1, len(model_predictor_features)))
                        for i, feat in enumerate(model_predictor_features):
                            if feat in scaler_X_features:
                                idx = scaler_X_features.index(feat)
                                scaled_for_model[0, i] = scaled_vals[0, idx]
                            else:
                                scaled_for_model[0, i] = 0.0

                        # Warn about extra scaler features not used by the model
                        extra_scaler_feats = [f for f in (scaler_X_features or []) if f not in model_predictor_features]
                        if extra_scaler_feats:
                            logger.warning(f"Scaler_X contains extra features not used by the model: {extra_scaler_feats}")
                            messages.warning(request, f"Note: predictor-scaler expects features {extra_scaler_feats} that are not used by the model; they were padded with zeros.")
                    else:
                        # No scaler available -> use raw values (numeric) in model order
                        try:
                            scaled_for_model = row[model_predictor_features].astype(float).values.reshape(1, -1)
                        except Exception as e:
                            logger.error(f"Failed to prepare model input without scaler: {e}")
                            messages.error(request, "Model input preparation failed (missing or non-numeric features).")
                            raise

                    # Predict scaled target (model was trained to predict scaled y)
                    pred_scaled = model.predict(scaled_for_model)[0]

                    # Inverse-transform prediction with scaler_y if available
                    prediction_original = None
                    if scaler_y is not None:
                        try:
                            prediction_original = float(scaler_y.inverse_transform([[pred_scaled]])[0, 0])
                        except Exception as e:
                            logger.error(f"Failed to inverse-transform predicted value: {e}")

                    # Derived planning metrics for the UI (use float to avoid template integer truncation)
                    predicted_students = float(prediction_original) if prediction_original is not None else float(pred_scaled)
                    teacher_ratio = 18.0
                    teacher_salary = 35000.0
                    ops_per_student = 2000.0

                    salary_cost = (predicted_students / teacher_ratio) * teacher_salary
                    ops_cost = predicted_students * ops_per_student
                    total_cost = salary_cost + ops_cost

                    prediction_result = {
                        'prediction_scaled': float(pred_scaled),
                        'prediction': predicted_students,
                        'model_used': getattr(model, '__class__', type(model)).__name__,
                        'features': row[model_predictor_features].iloc[0].tolist() if hasattr(row, 'iloc') else [],
                        'salary_cost': salary_cost,
                        'ops_cost': ops_cost,
                        'total_cost': total_cost,
                    }

                    # Audit log entry for this prediction
                    try:
                        import json as _json
                        from django.utils import timezone as _tz

                        model_metadata = _load_train_metadata() or {}

                        audit = {
                            'timestamp': _tz.now().isoformat(),
                            'user': getattr(request.user, 'username', 'anonymous'),
                            'model': model_metadata.get('model', getattr(model, '__class__', type(model)).__name__),
                            'model_metadata': model_metadata,
                            'input_features': {f: float(row.iloc[0][f]) if f in row.columns else None for f in list(row.columns)},
                            'prediction_scaled': float(pred_scaled),
                            'prediction_original': float(prediction_original) if prediction_original is not None else None,
                        }

                        audit_logger = logging.getLogger('edurise.model_usage')
                        audit_logger.info(_json.dumps(audit))
                    except Exception as e:
                        logger.error(f"Failed to write prediction audit log: {e}")

                    # Notification removed - user prefers silent prediction display
                except Exception as e:
                    logger.error(f"Error during model prediction: {e}")
                    messages.error(request, f"Prediction failed: {e}")
        else:
            messages.error(request, "Please correct errors in the form.")
    else:
        form = InstitutionsPredictionForm()

    return render(request, 'institutions/prediction.html', {
        'form': form,
        'prediction_result': prediction_result,
        'model_loaded': model is not None
    })
 
