from django.test import TestCase
from .models import Institution


class InstitutionModelTest(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(
            name="Test School",
            nombre_classes_2009=10,
            eleves_premier=100,
            eleves_superieur=50,
            latitude=48.8566,
            longitude=2.3522,
            cluster=1
        )
    
    def test_institution_creation(self):
        self.assertEqual(self.institution.name, "Test School")
        self.assertEqual(self.institution.cluster, 1)
    
    def test_total_students(self):
        self.assertEqual(self.institution.total_students, 150)
    
    def test_get_cluster_name(self):
        self.assertEqual(self.institution.get_cluster_name(), "Medium-to-Large Institutions")
 
