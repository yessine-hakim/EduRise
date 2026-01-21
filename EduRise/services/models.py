from django.db import models
from django.conf import settings

class PredictionHistory(models.Model):
    """
    Stores history of service predictions for users.
    """
    MODEL_CHOICES = [
        ('restauration', 'Restauration'),
        ('hebergement', 'Hebergement'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prediction_history')
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES)
    input_data = models.JSONField(help_text="Raw input values from the form")
    prediction_result = models.JSONField(help_text="Stored prediction result and probabilities")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Prediction Histories"

    def __str__(self):
        return f"{self.user.username} - {self.model_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
 
