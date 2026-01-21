from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
import csv
import os
from django.conf import settings
from django.utils.decorators import method_decorator
from .forms import ULISForm
from .ml_predictor import predict_ulis_demand
from . import cluster_model
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class ULISPredictionView(View):
    """
    View for ULIS demand prediction with form
    """
    template_name = 'ulis/ulis_prediction.html'
    
    def get(self, request):
        form = ULISForm()
        # Get prediction history from session
        prediction_history = request.session.get('ulis_prediction_history', [])
        
        context = {
            'form': form,
            'prediction': None,
            'prediction_history': prediction_history
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = ULISForm(request.POST)
        prediction_result = None
        error_message = None
        success = False
        
        if form.is_valid():
            data = form.cleaned_data
            
            input_data = {
                "Nombre_classes_2024": data["Nombre_classes_2024"],
                "Nombre_eleves_2024": data["Nombre_eleves_2024"],
                "Type_etablissement": data["Type_etablissement"],
                "libelle_nature": data["libelle_nature"],
                "Statut_public_prive": data["Statut_public_prive"],
                "Restauration": data["Restauration"],
            }
            
            # Call ML predictor
            prediction_result = predict_ulis_demand(input_data)
            
            if "error" in prediction_result:
                error_message = prediction_result["error"]
                logger.error(f"ULIS Prediction error: {error_message}")
            else:
                success = True
                logger.info(f"Successful ULIS prediction: {prediction_result}")
                
                # Store in history
                prediction_history = request.session.get('ulis_prediction_history', [])
                prediction_history.insert(0, {
                    'prediction': prediction_result.get('prediction'),
                    'timestamp': str(prediction_result.get('timestamp', ''))
                })
                request.session['ulis_prediction_history'] = prediction_history[:10]  # Keep last 10
        
        # Get prediction history from session
        prediction_history = request.session.get('ulis_prediction_history', [])
        
        context = {
            'form': form,
            'prediction': prediction_result,
            'error': error_message,
            'success': success,
            'prediction_history': prediction_history
        }
        
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ULISClusterMapView(View):
    """
    View for ULIS clustering analysis and visualization
    """
    template_name = 'ulis/ulis_cluster_maps.html'
    
    def get(self, request):
        # Use local KMeans model to derive cluster summaries from department dataset
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        clusters_list, err = cluster_model.get_department_clusters(data_dir)

        # Assign simple priority labels to clusters based on avg_inclusif_prop
        try:
            if clusters_list:
                # sort cluster ids by avg_inclusif_prop ascending (low presence -> high priority)
                sorted_clusters = sorted(clusters_list, key=lambda x: x.get('avg_inclusif_prop', 0.0))
                n = len(sorted_clusters)
                # divide into thirds for High/Medium/Low priority (approx)
                for idx, c in enumerate(sorted_clusters):
                    if idx < n/3:
                        c['priority'] = 'High Priority'
                    elif idx < 2*n/3:
                        c['priority'] = 'Medium Priority'
                    else:
                        c['priority'] = 'Low Priority'
                # ensure clusters_list retains new priority values
                clusters_list = sorted(clusters_list, key=lambda x: x['cluster_id'])
        except Exception:
            # non-fatal: leave clusters_list as-is
            pass

        if err:
            # Fallback to static descriptions if dataset/model unavailable
            cluster_info = [
                {'cluster_id': 0, 'title': 'Cluster 0', 'label': 'Cluster 0', 'description': err},
            ]
        else:
            # Build human-friendly labels and descriptions, mark cluster with lowest avg_inclusif_prop
            # Find cluster with smallest avg_inclusif_prop
            min_prop = None
            min_cluster = None
            for c in clusters_list:
                if min_prop is None or c['avg_inclusif_prop'] < min_prop:
                    min_prop = c['avg_inclusif_prop']
                    min_cluster = c['cluster_id']

            cluster_info = []
            for c in clusters_list:
                cid = c['cluster_id']
                label = f"Cluster {cid}"
                desc = f"{c['count']} départements — avg inclusifs proportion: {c['avg_inclusif_prop']}"
                if cid == min_cluster:
                    desc += " — LOW ULIS PRESENCE (priority)"
                cluster_info.append({
                    'cluster_id': cid,
                    'title': label,
                    'label': label,
                    'description': desc
                })

        # Prepare maps list (static placeholders or future dynamic maps)
        maps = [
            {'title': 'ULIS Geographic Distribution', 'description': 'Geographic distribution of ULIS units across regions', 'file': 'maps/carte_vue_globale.html'},
            {'title': 'Enrollment Clusters', 'description': 'ULIS units grouped by enrollment size and demographics', 'file': 'maps/carte_clusters_concentration_cluster2.html'},
            {'title': 'Resource Distribution', 'description': 'ULIS units grouped by available resources and infrastructure', 'file': 'maps/carte_clusters_gradient.html'},
        ]

        context = {
            'clusters': cluster_info,
            'maps': maps
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ULISClusterDataView(View):
    """Return cluster summaries and geo points as JSON for the frontend map."""
    def get(self, request):
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        clusters_list, err = cluster_model.get_department_clusters(data_dir)

        # Load geo points from recommandations_nouvelles_institutions.csv (if available)
        points = []
        rec_path = os.path.join(data_dir, 'recommandations_nouvelles_institutions.csv')
        if os.path.exists(rec_path):
            try:
                with open(rec_path, encoding='utf-8') as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        lat = row.get('Latitude') or row.get('latitude')
                        lng = row.get('Longitude') or row.get('longitude')
                        if not lat or not lng:
                            continue
                        try:
                            latf = float(lat)
                            lngf = float(lng)
                        except Exception:
                            continue
                        # determine color by score if available
                        score_val = None
                        try:
                            score_val = float(row.get('Score_Priorite') or row.get('Score_Priorite_Pct') or row.get('Score_Priorite', '') or 0)
                        except Exception:
                            score_val = None

                        color = 'blue'
                        if score_val is not None:
                            if score_val >= 0.7:
                                color = 'red'
                            elif score_val >= 0.4:
                                color = 'orange'
                            else:
                                color = 'green'

                        points.append({
                            'lat': latf,
                            'lng': lngf,
                            'departement': row.get('Departement') or row.get('Nom_Departement') or '',
                            'type': row.get('Type_Recommande') or '',
                            'score': row.get('Score_Priorite') or '',
                            'color': color
                        })
            except Exception as e:
                logger.error('Failed to load recommandations points: %s', e)

        # Fallback: try zones_optimales_construction.csv
        if not points:
            opt_path = os.path.join(data_dir, 'zones_optimales_construction.csv')
            if os.path.exists(opt_path):
                try:
                    with open(opt_path, encoding='utf-8') as fh:
                        reader = csv.DictReader(fh)
                        for row in reader:
                            lat = row.get('Latitude_Optimale')
                            lng = row.get('Longitude_Optimale')
                            if not lat or not lng:
                                continue
                            try:
                                latf = float(lat)
                                lngf = float(lng)
                            except Exception:
                                continue
                            # Try to map priority to color
                            score_val = None
                            try:
                                score_val = float(row.get('Score_Priorite') or row.get('Priorite_Score') or 0)
                            except Exception:
                                score_val = None
                            color = 'blue'
                            if score_val is not None:
                                if score_val >= 0.7:
                                    color = 'red'
                                elif score_val >= 0.4:
                                    color = 'orange'
                                else:
                                    color = 'green'

                            points.append({
                                'lat': latf,
                                'lng': lngf,
                                'departement': row.get('Nom_Departement') or '',
                                'type': row.get('Priorite') or '',
                                'score': row.get('priorite') or '',
                                'color': color
                            })
                except Exception as e:
                    logger.error('Failed to load optimal zones points: %s', e)

        response = {
            'error': err,
            'clusters': clusters_list,
            'points': points
        }
        return JsonResponse(response, safe=True)


@method_decorator(login_required, name='dispatch')
class ULISClusterExportView(View):
    """Export prioritized points (departement, type, score, lat, lng, color) as CSV."""
    def get(self, request):
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        rec_path = os.path.join(data_dir, 'recommandations_nouvelles_institutions.csv')
        opt_path = os.path.join(data_dir, 'zones_optimales_construction.csv')

        rows = []
        source = None
        if os.path.exists(rec_path):
            source = rec_path
        elif os.path.exists(opt_path):
            source = opt_path

        if not source:
            return HttpResponse('No recommendations data available', status=404)

        # Accept optional min_score filter (e.g. ?min_score=0.7)
        min_score_param = request.GET.get('min_score')
        try:
            min_score = float(min_score_param) if min_score_param not in (None, '', 'all') else None
        except Exception:
            min_score = None

        try:
            with open(source, encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    # attempt to extract lat/lng and score
                    lat = row.get('Latitude') or row.get('Latitude_Optimale') or row.get('latitude')
                    lng = row.get('Longitude') or row.get('Longitude_Optimale') or row.get('longitude')
                    if not lat or not lng:
                        continue
                    try:
                        latf = float(lat)
                        lngf = float(lng)
                    except Exception:
                        continue

                    score_raw = row.get('Score_Priorite') or row.get('Score_Priorite_Pct') or row.get('Priorite') or ''
                    score = None
                    try:
                        score = float(score_raw)
                    except Exception:
                        score = None

                    # apply min_score filter if provided
                    if min_score is not None and (score is None or score < min_score):
                        continue

                    # compute color same as cluster-data
                    color = 'blue'
                    if score is not None:
                        if score >= 0.7:
                            color = 'red'
                        elif score >= 0.4:
                            color = 'orange'
                        else:
                            color = 'green'

                    rows.append({
                        'departement': row.get('Departement') or row.get('Nom_Departement') or row.get('Departement_Nom') or '',
                        'type': row.get('Type_Recommande') or row.get('Type') or '',
                        'score': score_raw,
                        'lat': latf,
                        'lng': lngf,
                        'color': color,
                    })

        except Exception as e:
            logger.error('Failed to prepare export CSV: %s', e)
            return HttpResponse('Internal server error', status=500)

        # Build CSV response
        filename = 'ulis_cluster_points.csv'
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.DictWriter(resp, fieldnames=['departement','type','score','lat','lng','color'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return resp
  
