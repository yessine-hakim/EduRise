from django.shortcuts import render
from django.views import View
from .forms import EnrollmentPredictionForm
from .ml_predictor import predict_growth_class, predict_cluster
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CombinedPredictionView(View):
    """
    Vue combinée: formulaire + carte interactive
    """
    template_name = 'enrollment/combined_prediction.html'
    
    def get(self, request):
        form = EnrollmentPredictionForm()
        # Récupérer l'historique des prédictions depuis la session
        prediction_history = request.session.get('prediction_history', [])
        
        context = {
            'form': form,
            'prediction': None,
            'cluster': None,
            'cluster_map': None,
            'prediction_history': prediction_history
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = EnrollmentPredictionForm(request.POST)
        
        if form.is_valid():
            data = {
                'Nombre_classes_2023': form.cleaned_data['Nombre_classes_2023'],
                'Eleves_Superieur': form.cleaned_data['Eleves_Superieur'],
                'Type_etablissement': form.cleaned_data['Type_etablissement'],
                'Statut_public_prive': form.cleaned_data['Statut_public_prive'],
                'libelle_nature': form.cleaned_data['libelle_nature'],
                'Hebergement': form.cleaned_data['Hebergement']
            }
            
            try:
                # Prédictions
                growth_prediction = predict_growth_class(data)
                cluster_prediction = predict_cluster(data)
                
                # Déterminer quelle carte afficher selon le cluster
                if isinstance(cluster_prediction, dict) and 'cluster' in cluster_prediction:
                    cluster_map = f'carte_clusters_concentration_cluster{cluster_prediction["cluster"]}.html'
                else:
                    cluster_map = None
                
                # Sauvegarder la prédiction dans l'historique de session
                prediction_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'growth_class': growth_prediction.get('class', 'N/A'),
                    'growth_label': growth_prediction.get('class_label', 'N/A')[:50] + '...' if len(growth_prediction.get('class_label', '')) > 50 else growth_prediction.get('class_label', 'N/A'),
                    'cluster': cluster_prediction.get('cluster', 'N/A'),
                    'cluster_label': cluster_prediction.get('cluster_label', 'N/A'),
                    'confidence': growth_prediction.get('confidence', 'N/A'),
                    'probabilities': growth_prediction.get('probabilities', {}),
                    'data': {
                        'classes': data['Nombre_classes_2023'],
                        'students': data['Eleves_Superieur'],
                        'type': data['Type_etablissement'],
                        'nature': data['libelle_nature']
                    }
                }
                
                # Récupérer et mettre à jour l'historique
                prediction_history = request.session.get('prediction_history', [])
                prediction_history.insert(0, prediction_entry)  # Ajouter au début
                # Garder seulement les 5 dernières prédictions
                prediction_history = prediction_history[:5]
                request.session['prediction_history'] = prediction_history
                
                context = {
                    'form': form,
                    'prediction': growth_prediction,
                    'cluster': cluster_prediction if isinstance(cluster_prediction, dict) and 'cluster' in cluster_prediction else None,
                    'cluster_map': cluster_map,
                    'data': data,
                    'prediction_history': prediction_history
                }
                return render(request, self.template_name, context)
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                # On error, re-render form with error message
                prediction_history = request.session.get('prediction_history', [])
                context = {
                    'form': form,
                    'prediction': {'error': 'Erreur lors de la prédiction. Vérifiez les données.'},
                    'cluster': None,
                    'cluster_map': None,
                    'prediction_history': prediction_history
                }
                return render(request, self.template_name, context)
        
        # Form invalid
        prediction_history = request.session.get('prediction_history', [])
        context = {
            'form': form,
            'prediction': None,
            'cluster': None,
            'cluster_map': None,
            'prediction_history': prediction_history
        }
        return render(request, self.template_name, context)

class ClusterMapView(View):
    """
    Vue pour afficher les cartes de clusters
    """
    template_name = 'enrollment/cluster_maps.html'
    
    def get(self, request):
        # Chemins vers les cartes HTML générées
        maps = [
            {
                'title': 'Concentration Cluster 0',
                'file': 'carte_clusters_concentration_cluster0.html',
                'description': 'Distribution géographique du cluster 0'
            },
            {
                'title': 'Concentration Cluster 1',
                'file': 'carte_clusters_concentration_cluster1.html',
                'description': 'Distribution géographique du cluster 1'
            },
            {
                'title': 'Concentration Cluster 2',
                'file': 'carte_clusters_concentration_cluster2.html',
                'description': 'Distribution géographique du cluster 2'
            },
            {
                'title': 'Vue d\'ensemble des clusters',
                'file': 'carte_clusters_overview_stacked.html',
                'description': 'Vue d\'ensemble de tous les clusters'
            },
            {
                'title': 'Gradient des clusters',
                'file': 'carte_clusters_gradient.html',
                'description': 'Visualisation en gradient'
            }
        ]
        
        context = {
            'maps': maps
        }
        return render(request, self.template_name, context) 
