import pandas as pd
from django.core.management.base import BaseCommand
from InstitutionPP.models import Institution
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Load institutions from CSV file with pre-computed clusters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='InstitutionPP/data/institutions_with_clusters.csv',
            help='Path to CSV file (relative to BASE_DIR)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of institutions to load (for testing)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing institutions before loading'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        limit = options['limit']
        clear = options['clear']
        
        # Build full path
        if not os.path.isabs(csv_path):
            csv_path = os.path.join(settings.BASE_DIR, csv_path)
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return
        
        self.stdout.write(f'Loading data from: {csv_path}')
        
        # Clear existing data if requested
        if clear:
            count = Institution.objects.count()
            Institution.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing institutions'))
        
        # Load CSV
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            self.stdout.write(f'Loaded CSV with {len(df)} rows')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading CSV: {e}'))
            return
        
        # Required columns for pre-computed clusters CSV
        required_cols = [
            'name',
            'nombre_classes_2009',
            'eleves_premier',
            'eleves_superieur',
            'latitude',
            'longitude',
            'cluster'
        ]
        
        # Check if columns exist
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            self.stdout.write(self.style.ERROR(f'Missing columns: {missing}'))
            return
        
        # Drop NaN
        df_clean = df.dropna()
        self.stdout.write(f'After removing NaN: {len(df_clean)} rows')
        
        # Apply limit if specified
        if limit:
            df_clean = df_clean.head(limit)
            self.stdout.write(f'Limited to {limit} rows')
        
        # Load institutions in batches
        created = 0
        errors = 0
        batch_size = 1000
        institutions = []
        
        self.stdout.write('Loading institutions...')
        
        for idx, row in df_clean.iterrows():
            try:
                institutions.append(Institution(
                    name=row['name'] if pd.notna(row['name']) else None,
                    nombre_classes_2009=float(row['nombre_classes_2009']),
                    eleves_premier=float(row['eleves_premier']),
                    eleves_superieur=float(row['eleves_superieur']),
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    cluster=int(row['cluster'])
                ))
                
                # Bulk create every 1000 records
                if len(institutions) >= batch_size:
                    Institution.objects.bulk_create(institutions, ignore_conflicts=True)
                    created += len(institutions)
                    self.stdout.write(f'  Loaded {created} institutions...')
                    institutions = []
                    
            except Exception as e:
                errors += 1
                if errors < 10:  # Only show first 10 errors
                    self.stdout.write(self.style.WARNING(f'Error on row {idx}: {e}'))
        
        # Save remaining institutions
        if institutions:
            Institution.objects.bulk_create(institutions, ignore_conflicts=True)
            created += len(institutions)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Completed! Loaded {created} institutions ({errors} errors)'
        ))
        
        # Show cluster distribution
        total = Institution.objects.count()
        self.stdout.write(f'\nTotal institutions in database: {total}')
        self.stdout.write('\nCluster distribution:')
        for i in range(4):
            count = Institution.objects.filter(cluster=i).count()
            pct = (count / total * 100) if total > 0 else 0
            self.stdout.write(f'  Cluster {i}: {count:6d} ({pct:5.2f}%)')

 
