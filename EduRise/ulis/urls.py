from django.urls import path
from .views import ULISPredictionView, ULISClusterMapView, ULISClusterExportView, ULISClusterDataView

app_name = 'ulis'

urlpatterns = [
    # ULIS prediction with form
    path("predict/", ULISPredictionView.as_view(), name="ulis_predict"),
    
    # ULIS cluster maps visualization
    path("cluster-maps/", ULISClusterMapView.as_view(), name="ulis_cluster_maps"),
    
    # ULIS cluster data (JSON)
    path("cluster-data/", ULISClusterDataView.as_view(), name="ulis_cluster_data"),

    # ULIS cluster export (CSV)
    path("cluster-export/", ULISClusterExportView.as_view(), name="ulis_cluster_export"),
]
   
