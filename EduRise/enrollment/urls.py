from django.urls import path
from . import views

app_name = 'enrollment'

urlpatterns = [
    # Vos URLs existantes...
    
    # Vue combinée: formulaire + carte interactive
    path('predict-with-map/', views.CombinedPredictionView.as_view(), name='predict_with_map'),
    
    # Visualisation des cartes de clusters
    path('cluster-maps/', views.ClusterMapView.as_view(), name='cluster_maps'),
] 
