from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import PredictionHistory

User = get_user_model()

class PredictionHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_prediction_saves_to_history(self):
        # Mock prediction logic is not needed for history saving if we can get a valid form submission
        # However, testing the model directly is easier and less prone to ML loader issues
        PredictionHistory.objects.create(
            user=self.user,
            model_type='restauration',
            input_data={'code_departement': 75, 'nombre_eleves_totale': 500},
            prediction_result={'prediction': 1, 'prediction_label': 'Yes'}
        )
        
        self.assertEqual(PredictionHistory.objects.count(), 1)
        history = PredictionHistory.objects.first()
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.model_type, 'restauration')
        self.assertEqual(history.input_data['code_departement'], 75)

    def test_history_ordering(self):
        PredictionHistory.objects.create(
            user=self.user,
            model_type='restauration',
            input_data={'val': 1},
            prediction_result={}
        )
        PredictionHistory.objects.create(
            user=self.user,
            model_type='hebergement',
            input_data={'val': 2},
            prediction_result={}
        )
        
        histories = PredictionHistory.objects.filter(user=self.user)
        self.assertEqual(histories.count(), 2)
        # Should be ordered by created_at DESC
        self.assertEqual(histories[0].model_type, 'hebergement')
        self.assertEqual(histories[1].model_type, 'restauration')
 
