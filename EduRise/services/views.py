from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import ServicesPredictionForm
from .models import PredictionHistory
from .ml_loader import get_ml_client
import logging
import os
import pandas as pd
import json
from django.conf import settings
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)


@login_required
def institutions_list(request):
    """Institutions ML module view"""
    return render(request, 'institutions/institutions.html')


@login_required
def enrollment_list(request):
    """Enrollment ML module view"""
    return render(request, 'enrollment/enrollment.html')


@login_required
def services_list(request):
    """
    Services ML module view with prediction functionality.
    
    Handles both GET (display form) and POST (process prediction) requests.
    Uses pre-trained ML models to predict Restauration or Hebergement services.
    """
    form = None
    prediction_result = None
    
    
    # ML Models are hosted on external service (checked on prediction)

    
    if request.method == 'POST':
        # Process form submission
        form = ServicesPredictionForm(request.POST)
        
        if form.is_valid():
            try:
                # Prepare payload for API
                # Extract encoded features from form (returns list of numbers)
                features_list = form.get_feature_array()
                
                # API Call via ML Client
                ml_client = get_ml_client()
                
                # Map list to dict using feature order
                features_dict = dict(zip(ml_client.FEATURE_ORDER, features_list))

                model_type = form.cleaned_data['model_type']
                
                # API Call via ML Client
                ml_client = get_ml_client()
                prediction_result = ml_client.predict(features_dict, model_type)
                
                # Convert probability list to dictionary for easier template access if needed
                # The API returns "probability": [p0, p1] or null
                if prediction_result.get('probability'):
                    prob_list = prediction_result['probability']
                    prediction_result['probability'] = {
                        0: prob_list[0],
                        1: prob_list[1]
                    }
                
                # Add additional context for display
                prediction_result['features_used'] = features_dict
                
                # Log successful prediction
                logger.info(f"Prediction made: {model_type} -> {prediction_result['prediction']}")
                
                # Save to history
                try:
                    # Collect all form field values
                    input_data = {field: form.cleaned_data[field] for field in form.fields if field != 'model_type'}
                    
                    PredictionHistory.objects.create(
                        user=request.user,
                        model_type=model_type,
                        input_data=input_data,
                        prediction_result=prediction_result
                    )
                    logger.info("Prediction history saved")
                except Exception as e:
                    logger.error(f"Failed to save prediction history: {e}")

                # Add success message (auto-dismisses after 5 seconds)
                messages.success(request, f"Prediction completed successfully using {model_type.title()} model.", extra_tags='auto-dismiss')
                
            except ValueError as e:
                logger.error(f"Validation error during prediction: {e}")
                messages.error(request, f"Invalid input: {e}")
                prediction_result = None
            except Exception as e:
                logger.error(f"Error during prediction: {e}")
                messages.error(request, "Prediction service unavailable. Please check the connection.")
                prediction_result = None
        else:
            # Form validation failed
            messages.error(request, "Please correct the errors in the form.")
    else:
        # GET request - display empty form
        form = ServicesPredictionForm()
    
    # Fetch prediction history for the current user (limit to 10 most recent)
    history = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    return render(request, 'services/services.html', {
        'form': form,
        'prediction_result': prediction_result,
        'history': history
    })


@login_required
def ulis_list(request):
    """ULIS ML module view"""
    return render(request, 'ulis/ulis.html')


@login_required
def recommendations_view(request):
    """
    View for the new Services Recommendations page.
    Visualizes recommendations and clustering on a map.
    Optimized to slice data server-side and paginate the rest.
    """
    try:
        ml_engine_path = os.path.join(settings.BASE_DIR, 'services', 'ml_engine')
        
        # Load CSVs
        # Use dtype to prevent department code issues initially
        df_rest = pd.read_csv(os.path.join(ml_engine_path, 'restaurant_recommendations.csv'))
        df_heb = pd.read_csv(os.path.join(ml_engine_path, 'hebergement_recommendations.csv'))
        df_clusters = pd.read_csv(os.path.join(ml_engine_path, 'ml_services_clustering_departments_results.csv'))

        # Helper to clean department codes
        def clean_dep_code(val):
            val_str = str(val)
            if len(val_str) == 1 and val_str.isdigit():
                return '0' + val_str
            return val_str

        # Standardize DataFrames
        df_rest['Service_Type'] = 'Restauration'
        df_heb['Service_Type'] = 'Hebergement'
        
        # 1. Prepare Data for MAP (Top 20 Recommendations Total)
        # Combine both datasets to find the absolute top 20
        # Ensure we have the necessary columns
        columns_needed = ['Nom_etablissement', 'Type_etablissement', 'Libelle_departement', 'latitude', 'longitude', 'overall_priority_score', 'Service_Type']
        
        # Select and Rename columns if needed to match standardized list
        # For Restaurant
        df_rest['overall_priority_score'] = df_rest['rest_priority_score']
        # For Hebergement
        df_heb['overall_priority_score'] = df_heb['heberg_priority_score']

        rest_subset = df_rest[columns_needed].copy()
        heb_subset = df_heb[columns_needed].copy()
        
        combined_df = pd.concat([rest_subset, heb_subset])
        
        # Sort by Priority Score Descending
        combined_df = combined_df.sort_values(by='overall_priority_score', ascending=False)
        
        # 1. Prepare Data for MAP (Top 20 Recommendations PER TYPE)
        # Sort by Priority Score Descending
        combined_df = combined_df.sort_values(by='overall_priority_score', ascending=False)
        
        # Split by type to ensure equal representation
        rest_all = combined_df[combined_df['Service_Type'] == 'Restauration']
        heb_all = combined_df[combined_df['Service_Type'] == 'Hebergement']
        
        # Take Top 20 of each
        top_rest = rest_all.head(20)
        top_heb = heb_all.head(20)
        
        # Combine for map
        map_recommendations_df = pd.concat([top_rest, top_heb])
        
        # Convert to list of dicts for JSON
        map_recommendations = map_recommendations_df.replace({float('nan'): None}).to_dict(orient='records')
        
        # 2. Prepare Data for TABLE (Remaining Recommendations)
        # Exclude the top 20 from the main table dataset (or show all? User said "Remaining recommendations", implies separate)
        # Let's show the remaining ones.
        remaining_df = combined_df.iloc[50:]

        # Prepare Cluster Data & Mapping
        df_clusters['Code_departement'] = df_clusters['Code_departement'].apply(clean_dep_code)
        # Create mapping for filtering (Code -> Libelle)
        dept_map = dict(zip(df_clusters['Code_departement'], df_clusters['Libelle_departement']))

        # Filter Logic for Table
        filter_dept = request.GET.get('department')
        filter_type = request.GET.get('service_type')
        
        if filter_dept:
            # Map code to Libelle for filtering since CSVs only have Libelle
            target_libelle = dept_map.get(filter_dept)
            if target_libelle:
                remaining_df = remaining_df[remaining_df['Libelle_departement'] == target_libelle]

        
        if filter_type:
            # Map "restauration" / "hebergement" to "Restauration" / "Hebergement"
            if filter_type.lower() == 'restauration':
                remaining_df = remaining_df[remaining_df['Service_Type'] == 'Restauration']
            elif filter_type.lower() == 'hebergement':
                 remaining_df = remaining_df[remaining_df['Service_Type'] == 'Hebergement']
        
        # Pagination
        paginator = Paginator(remaining_df.to_dict(orient='records'), 20) # 20 per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 3. Prepare Cluster Data for Map
        # Already cleaned above for mapping
        clusters_data = df_clusters[['Code_departement', 'Libelle_departement', 'Assigned_Cluster', 'Service_Coverage']].to_dict(orient='records')
        
        # Get list of Departments for Filter Dropdown
        departments = sorted(df_clusters[['Code_departement', 'Libelle_departement']].drop_duplicates().to_dict(orient='records'), key=lambda x: x['Code_departement'])

        context = {
            'map_recommendations': json.dumps(map_recommendations),
            'clusters': json.dumps(clusters_data),
            'page_obj': page_obj,
            'departments': departments,
            # Pass filter values back to context to keep dropdowns selected
            'selected_dept': filter_dept,
            'selected_type': filter_type,
        }
    except Exception as e:
        logger.error(f"Error loading recommendation data: {e}")
        messages.error(request, f"Error loading data: {e}")
        # Provide safe defaults so the template does not error when data loading fails
        empty_paginator = Paginator([], 1)
        safe_page = empty_paginator.get_page(1)
        context = {
            'map_recommendations': '[]',
            'clusters': '[]',
            'page_obj': safe_page,
            'departments': [],
            'selected_dept': None,
            'selected_type': None,
        }

    return render(request, 'services/recommendations.html', context)


@login_required
def clustering_view(request):
    """
    View for predicting service importance clusters.
    """
    form = None
    prediction_result = None
    
    # Cluster Interpretations from User
    cluster_interpretations = {
        0: {
            "title": "Critical Restauration",
            "description": "Very low restauration availability with high pressure. Hébergement availability is limited but not critical.",
            "action": "Service importance indicates a critical need to improve restauration services.",
            "level": "danger" # CSS class suffix
        },
        1: {
            "title": "Stable",
            "description": "Balanced availability for both restauration and hébergement, with no significant pressure.",
            "action": "Service importance is stable, no urgent intervention required.",
            "level": "success"
        },
        2: {
            "title": "Critical Hébergement",
            "description": "Very strong hébergement availability but extremely high demand, while restauration remains weak.",
            "action": "Service importance indicates hébergement capacity management is critical, and restauration requires improvement.",
            "level": "warning"
        }
    }

    if request.method == 'POST':
        from .forms import ClusteringForm
        form = ClusteringForm(request.POST)
        
        if form.is_valid():
            try:
                # Prepare features for API
                features_dict = form.get_encoded_features()
                
                # API Call via ML Client
                ml_client = get_ml_client()
                # model_type="clustering"
                result_data = ml_client.predict(features_dict, "clustering") 
                
                cluster_id = result_data['prediction']
                interpretation = cluster_interpretations.get(cluster_id, {
                    "title": "Unknown Cluster",
                    "description": "No specific interpretation available for this cluster.",
                    "action": "Please review inputs.",
                    "level": "secondary"
                })
                
                prediction_result = {
                    "cluster_id": cluster_id, # Keep internal but don't show user if not requested, used for logic
                    "interpretation": interpretation,
                    "features_used": features_dict # For display if needed
                }
                
                messages.success(request, "Clustering prediction completed successfully.", extra_tags='auto-dismiss')
                
            except Exception as e:
                logger.error(f"Error during clustering prediction: {e}")
                messages.error(request, f"Prediction service unavailable: {e}")
                prediction_result = None
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        from .forms import ClusteringForm
        form = ClusteringForm()

    return render(request, 'services/clustering.html', {
        'form': form,
        'prediction_result': prediction_result
    })

@login_required
def recommendations_api(request):
    """
    API endpoint for AJAX filtering of recommendations.
    Returns JSON data with filtered recommendations and pagination info.
    """
    try:
        ml_engine_path = os.path.join(settings.BASE_DIR, 'services', 'ml_engine')
        
        # Load CSVs
        df_rest = pd.read_csv(os.path.join(ml_engine_path, 'restaurant_recommendations.csv'))
        df_heb = pd.read_csv(os.path.join(ml_engine_path, 'hebergement_recommendations.csv'))
        # Load Clusters for mapping
        df_clusters = pd.read_csv(os.path.join(ml_engine_path, 'ml_services_clustering_departments_results.csv'))

        # Helper to clean department codes
        def clean_dep_code(val):
            val_str = str(val)
            if len(val_str) == 1 and val_str.isdigit():
                return '0' + val_str
            return val_str

        # Standardize DataFrames
        df_rest['Service_Type'] = 'Restauration'
        df_heb['Service_Type'] = 'Hebergement'

        # Combine both datasets
        columns_needed = ['Nom_etablissement', 'Type_etablissement', 'Libelle_departement', 'latitude', 'longitude', 'overall_priority_score', 'Service_Type']
        
        # Standardize Score Column
        df_rest['overall_priority_score'] = df_rest['rest_priority_score']
        df_heb['overall_priority_score'] = df_heb['heberg_priority_score']

        rest_subset = df_rest[columns_needed].copy()
        heb_subset = df_heb[columns_needed].copy()
        combined_df = pd.concat([rest_subset, heb_subset])

        # Sort by Priority Score Descending
        combined_df = combined_df.sort_values(by='overall_priority_score', ascending=False)

        # Split by type to ensure equal representation for map
        rest_all = combined_df[combined_df['Service_Type'] == 'Restauration']
        heb_all = combined_df[combined_df['Service_Type'] == 'Hebergement']
        top_rest = rest_all.head(20)
        top_heb = heb_all.head(20)

        # For table, exclude top items - show remaining (matching original view logic)
        remaining_df = combined_df.iloc[50:]

        # Filter Logic
        filter_dept = request.GET.get('department')
        filter_type = request.GET.get('service_type')

        if filter_dept:
            # Map code to Libelle
            df_clusters['Code_departement'] = df_clusters['Code_departement'].apply(clean_dep_code)
            dept_map = dict(zip(df_clusters['Code_departement'], df_clusters['Libelle_departement']))
            target_libelle = dept_map.get(filter_dept)
            if target_libelle:
                remaining_df = remaining_df[remaining_df['Libelle_departement'] == target_libelle]


        if filter_type:
            if filter_type.lower() == 'restauration':
                remaining_df = remaining_df[remaining_df['Service_Type'] == 'Restauration']
            elif filter_type.lower() == 'hebergement':
                remaining_df = remaining_df[remaining_df['Service_Type'] == 'Hebergement']

        # Pagination
        paginator = Paginator(remaining_df.to_dict(orient='records'), 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Prepare response data
        items = []
        for item in page_obj:
            # Replace NaN with None for JSON serialization
            clean_item = {}
            for k, v in item.items():
                if isinstance(v, float) and pd.isna(v):
                    clean_item[k] = None
                else:
                    clean_item[k] = v
            items.append(clean_item)

        return JsonResponse({
            'items': items,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages,
            'total_items': page_obj.paginator.count,
        })

    except Exception as e:
        logger.error(f"Error in recommendations API: {e}")
        return JsonResponse({'error': str(e)}, status=500)

 
