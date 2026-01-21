# InstitutionPP - Institution Clustering & Classification

This Django app provides machine learning-based clustering and classification for educational institutions.

## Features

- **Institution Clustering**: K-Means clustering (4 clusters) using HuggingFace API
  - Cluster 0: Small Metropolitan Schools (1.7%)
  - Cluster 1: Medium-to-Large Institutions (34.0%)
  - Cluster 2: Standard Small Schools (62.6%)
  - Cluster 3: Overseas Territories (1.7%)

- **Public/Private Classification**: Random Forest classification via HuggingFace API
  - Predicts if an institution is public (0) or private (1)
  - Shows confidence percentage

## Architecture

This app uses a lightweight architecture:
- **HuggingFace Space**: https://YassineM05-Projet.hf.space (ML models hosted externally)
- **Local App**: Only handles UI and database
- **API Communication**: HTTP requests for predictions

## Integration Notes

All files specific to this module are contained in the `InstitutionPP/` folder.

Changes to existing project files are marked with `########maalej######`:
- `edurise/settings.py`: Added app to INSTALLED_APPS and HUGGINGFACE_API_URL setting
- `edurise/urls.py`: Added URL pattern for `/institutionpp/`
- `requirements.txt`: Documented required dependencies (already satisfied)

## Data Files

Located in `InstitutionPP/data/`:
- `ml_df_public_private_imbalance.csv`: Main dataset with institution features
- `institution_id_row_mapping.csv`: Institution names mapping

## Usage

### 1. Run Migrations

```bash
python manage.py makemigrations InstitutionPP
python manage.py migrate InstitutionPP
```

### 2. Load Institutions (Optional)

Load institutions from CSV and auto-predict clusters:

```bash
# Load first 100 for testing
python manage.py load_institutions --limit 100

# Clear and load all data
python manage.py load_institutions --clear

# Load from custom CSV
python manage.py load_institutions --csv path/to/your/file.csv
```

### 3. Access the Application

- **Clustering**: http://localhost:8000/institutionpp/
- **Classification**: http://localhost:8000/institutionpp/classify/
- **Cluster Details**: http://localhost:8000/institutionpp/cluster/0/ (0-3)

### 4. Add Institutions via UI

1. Go to the clustering page
2. Fill in the form with institution details
3. Submit - cluster will be auto-predicted using HuggingFace API

## API Endpoints Used

### Cluster Prediction
- **URL**: `{HUGGINGFACE_API_URL}/predict/cluster`
- **Method**: POST
- **Payload**:
  ```json
  {
    "nombre_classes_2009": 10.0,
    "eleves_premier": 150.0,
    "eleves_superieur": 200.0,
    "latitude": 48.8566,
    "longitude": 2.3522
  }
  ```

### Public/Private Classification
- **URL**: `{HUGGINGFACE_API_URL}/predict/public-private`
- **Method**: POST
- **Payload**:
  ```json
  {
    "nombre_classes_2009": 10.0,
    "eleves_premier": 150.0,
    "eleves_superieur": 200.0,
    "latitude": 48.8566,
    "longitude": 2.3522,
    "restauration": 1,
    "hebergement": 0,
    "ulis": 1
  }
  ```

## Models

### Institution Model
- `nombre_classes_2009`: Number of classes
- `eleves_premier`: Primary students count
- `eleves_superieur`: Secondary students count
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `cluster`: Assigned cluster (0-3)
- `name`: Optional institution name
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Dependencies

- Django >= 4.2
- pandas >= 2.0.0
- requests >= 2.31.0

## Original Source

This module was integrated from `projet4.0/django_clustering/clustering_app/`.
 
