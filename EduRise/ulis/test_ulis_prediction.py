"""
Tests for ULIS prediction module
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .ml_predictor import (
    validate_and_map_input,
    predict_ulis_demand,
    TYPE_ETABLISSEMENT_MAPPING,
    LIBELLE_NATURE_MAPPING,
    STATUT_PUBLIC_PRIVE_MAPPING,
    RESTAURATION_MAPPING,
)


class ULISPredictorValidationTest(unittest.TestCase):
    """Test input validation and mapping functions"""

    def test_valid_input_mapping(self):
        """Test valid input is properly mapped"""
        data = {
            "Nombre_classes_2024": 15,
            "Nombre_eleves_2024": 300,
            "Type_etablissement": "ECOLE",
            "libelle_nature": "ELEMENTAIRE",
            "Statut_public_prive": "PUBLIC",
            "Restauration": "OUI",
        }
        
        result = validate_and_map_input(data)
        
        self.assertEqual(result["Nombre_classes_2024"], 15)
        self.assertEqual(result["Nombre_eleves_2024"], 300)
        self.assertEqual(result["Type_etablissement"], 0)  # ECOLE maps to 0
        self.assertEqual(result["libelle_nature"], 1)  # ELEMENTAIRE maps to 1
        self.assertEqual(result["Statut_public_prive"], 0)  # PUBLIC maps to 0
        self.assertEqual(result["Restauration"], 1)  # OUI maps to 1

    def test_missing_required_field(self):
        """Test that missing required fields raise ValueError"""
        data = {
            "Nombre_classes_2024": 15,
            "Nombre_eleves_2024": 300,
            # Missing Type_etablissement
        }
        
        with self.assertRaises(ValueError):
            validate_and_map_input(data)

    def test_invalid_numeric_value(self):
        """Test that invalid numeric values raise ValueError"""
        data = {
            "Nombre_classes_2024": "invalid",
            "Nombre_eleves_2024": 300,
            "Type_etablissement": "ECOLE",
            "libelle_nature": "ELEMENTAIRE",
            "Statut_public_prive": "PUBLIC",
            "Restauration": "OUI",
        }
        
        with self.assertRaises(ValueError):
            validate_and_map_input(data)

    def test_invalid_choice_value(self):
        """Test that invalid choice values raise ValueError"""
        data = {
            "Nombre_classes_2024": 15,
            "Nombre_eleves_2024": 300,
            "Type_etablissement": "INVALID",
            "libelle_nature": "ELEMENTAIRE",
            "Statut_public_prive": "PUBLIC",
            "Restauration": "OUI",
        }
        
        with self.assertRaises(ValueError):
            validate_and_map_input(data)


class ULISFormTest(TestCase):
    """Test ULIS form functionality"""

    def test_form_renders_correctly(self):
        """Test that form renders with all required fields"""
        from .forms import ULISForm
        form = ULISForm()
        
        self.assertIn("Nombre_classes_2024", form.fields)
        self.assertIn("Nombre_eleves_2024", form.fields)
        self.assertIn("Type_etablissement", form.fields)
        self.assertIn("libelle_nature", form.fields)
        self.assertIn("Statut_public_prive", form.fields)
        self.assertIn("Restauration", form.fields)

    def test_valid_form_submission(self):
        """Test valid form data passes validation"""
        from .forms import ULISForm
        
        data = {
            "Nombre_classes_2024": 15,
            "Nombre_eleves_2024": 300,
            "Type_etablissement": "ECOLE",
            "libelle_nature": "ELEMENTAIRE",
            "Statut_public_prive": "PUBLIC",
            "Restauration": "OUI",
        }
        
        form = ULISForm(data=data)
        self.assertTrue(form.is_valid())


class ULISViewTest(TestCase):
    """Test ULIS prediction view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_view_requires_login(self):
        """Test that view requires authentication"""
        response = self.client.get("/ulis/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_authenticated_user_can_access_form(self):
        """Test that authenticated user can access the form"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/ulis/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @patch("ulis.ml_predictor.send_prediction_request")
    def test_form_submission_with_mock_prediction(self, mock_request):
        """Test form submission with mocked ML prediction"""
        mock_request.return_value = {
            "prediction": "High demand",
            "confidence": 85.5
        }
        
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "Nombre_classes_2024": 15,
            "Nombre_eleves_2024": 300,
            "Type_etablissement": "ECOLE",
            "libelle_nature": "ELEMENTAIRE",
            "Statut_public_prive": "PUBLIC",
            "Restauration": "OUI",
        }
        
        response = self.client.post("/ulis/", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["success"])


if __name__ == "__main__":
    unittest.main()
 
