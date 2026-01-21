from django.urls import path
from . import views

urlpatterns = [
    path('', views.institution_list, name='institution_list'),
    path('cluster/<int:cluster_id>/', views.cluster_details, name='cluster_details'),
    path('classify/', views.classify_institution, name='classify_institution'),
]
 
