from django.urls import path
from . import views

app_name = 'institutions'

urlpatterns = [
    path('recommendations/', views.recommendations, name='institutions_recommendations'),
    path('prediction/', views.prediction, name='prediction'),
    path('clusters/', views.clusters_overview, name='clusters_overview'),
]
 
