from django.core.management.base import BaseCommand
from InstitutionPP.models import Institution
import csv


class Command(BaseCommand):
    help = 'Export all institutions with clusters to CSV'

    def handle(self, *args, **options):
        output_file = 'InstitutionPP/data/institutions_with_clusters.csv'
        
        institutions = Institution.objects.all().values(
            'name', 'nombre_classes_2009', 'eleves_premier', 
            'eleves_superieur', 'latitude', 'longitude', 'cluster'
        )
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'nombre_classes_2009', 'eleves_premier', 
                'eleves_superieur', 'latitude', 'longitude', 'cluster'
            ])
            writer.writeheader()
            
            count = 0
            for inst in institutions:
                writer.writerow(inst)
                count += 1
                if count % 10000 == 0:
                    self.stdout.write(f'Exported {count} institutions...')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Exported {count} institutions to {output_file}'))
 
