from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Institutions
    path('institutions/', views.institutions_list, name='institutions_list'),
    
    # Enrollment
    path('enrollment/', views.enrollment_list, name='enrollment_list'),
    
    # Services
    path('services/', views.services_list, name='services_list'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('recommendations/api/', views.recommendations_api, name='recommendations_api'),
    path('clustering/', views.clustering_view, name='clustering_view'),
    
    # ULIS
    path('ulis/', views.ulis_list, name='ulis_list'),
]
 
