from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Institution
from .forms import InstitutionForm, ClassificationForm
from .utils import predict_cluster, predict_public_private
import logging

logger = logging.getLogger(__name__)


def is_institution_admin_or_manager(user):
    return user.is_authenticated and (user.is_admin() or user.is_institution_manager())


@login_required
@user_passes_test(is_institution_admin_or_manager)
def institution_list(request):
    """Display all institutions and handle new institution creation."""
    
    # Handle form submission
    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            try:
                # Create instance without saving
                institution = form.save(commit=False)
                
                # Predict cluster using the trained model
                cluster = predict_cluster(
                    nombre_classes=institution.nombre_classes_2009,
                    eleves_premier=institution.eleves_premier,
                    eleves_superieur=institution.eleves_superieur,
                    latitude=institution.latitude,
                    longitude=institution.longitude
                )
                
                # Assign cluster and save
                institution.cluster = cluster
                institution.save()
                
                cluster_name = institution.get_cluster_name()
                messages.success(
                    request,
                    f'Institution added successfully! Assigned to: {cluster_name}'
                )
                return redirect('institution_list')
                
            except Exception as e:
                logger.error(f"Error predicting cluster: {e}")
                messages.error(
                    request,
                    f'Error processing institution: {str(e)}'
                )
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InstitutionForm()
    
    # Get all institutions
    institutions = Institution.objects.all()
    
    # Apply cluster filter
    cluster_filter = request.GET.get('cluster', '')
    if cluster_filter and cluster_filter.isdigit():
        cluster_id = int(cluster_filter)
        if cluster_id in [0, 1, 2, 3]:
            institutions = institutions.filter(cluster=cluster_id)
    
    # Add pagination
    paginator = Paginator(institutions, 50)  # Show 50 institutions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get cluster statistics
    cluster_stats = {}
    for i in range(4):
        count = Institution.objects.filter(cluster=i).count()
        cluster_stats[i] = {
            'count': count,
            'percentage': (count / Institution.objects.count() * 100) if Institution.objects.count() > 0 else 0
        }
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'institutions': page_obj,
        'total_count': institutions.count(),
        'cluster_stats': cluster_stats,
        'cluster_filter': cluster_filter,
    }
    
    return render(request, 'InstitutionPP/institution_list.html', context)


@login_required
@user_passes_test(is_institution_admin_or_manager)
def cluster_details(request, cluster_id):
    """Display institutions in a specific cluster with filtering."""
    
    if cluster_id not in [0, 1, 2, 3]:
        messages.error(request, 'Invalid cluster ID')
        return redirect('institution_list')
    
    institutions = Institution.objects.filter(cluster=cluster_id)
    
    # Get filter parameters
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')
    
    # Apply search filter
    if search:
        institutions = institutions.filter(name__icontains=search)
    
    # Apply sorting
    valid_sort_fields = {
        'id': 'id',
        'name': 'name',
        'classes': 'nombre_classes_2009',
        'primary': 'eleves_premier',
        'secondary': 'eleves_superieur',
        'total': 'eleves_premier',  # Will compute total
        'date': 'created_at',
    }
    
    if sort_by in valid_sort_fields:
        sort_field = valid_sort_fields[sort_by]
        if order == 'desc':
            sort_field = f'-{sort_field}'
        institutions = institutions.order_by(sort_field)
    
    # Pagination
    paginator = Paginator(institutions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cluster_names = {
        0: "Small Metropolitan Schools",
        1: "Medium-to-Large Institutions",
        2: "Standard Small Schools",
        3: "Overseas Territories"
    }
    
    context = {
        'cluster_id': cluster_id,
        'cluster_name': cluster_names[cluster_id],
        'page_obj': page_obj,
        'institutions': page_obj,
        'total_count': institutions.count(),
        'search': search,
        'sort_by': sort_by,
        'order': order,
    }
    
    return render(request, 'InstitutionPP/cluster_details.html', context)


@login_required
@user_passes_test(is_institution_admin_or_manager)
def classify_institution(request):
    """Predict if an institution is public or private using HuggingFace API."""
    
    prediction_result = None
    
    if request.method == 'POST':
        form = ClassificationForm(request.POST)
        if form.is_valid():
            try:
                # Get form data
                form_data = form.cleaned_data
                
                # Predict public/private using HuggingFace API
                prediction, confidence = predict_public_private(form_data)
                
                # Store result
                prediction_result = {
                    'prediction': prediction,
                    'label': 'Private' if prediction == 1 else 'Public',
                    'confidence': confidence
                }
                
                messages.success(
                    request,
                    f'Prediction: {prediction_result["label"]} institution (Confidence: {confidence:.1f}%)'
                )
                
            except Exception as e:
                logger.error(f"Error in classification: {e}")
                messages.error(
                    request,
                    f'Error processing classification: {str(e)}. Make sure HuggingFace API is available.'
                )
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassificationForm()
    
    context = {
        'form': form,
        'prediction_result': prediction_result,
        'model_missing': False,  # Models are on HuggingFace, not local
    }
    
    return render(request, 'InstitutionPP/classify.html', context)
 
