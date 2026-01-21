from django.db import models


class Institution(models.Model):
    """Model representing an educational institution."""
    
    # Feature fields used for clustering
    nombre_classes_2009 = models.FloatField(
        verbose_name="Number of Classes (2009)",
        help_text="Number of classes in the institution"
    )
    eleves_premier = models.FloatField(
        verbose_name="Primary Students",
        help_text="Number of primary/elementary students"
    )
    eleves_superieur = models.FloatField(
        verbose_name="Secondary Students",
        help_text="Number of secondary/higher education students"
    )
    latitude = models.FloatField(
        verbose_name="Latitude",
        help_text="Geographic latitude"
    )
    longitude = models.FloatField(
        verbose_name="Longitude",
        help_text="Geographic longitude"
    )
    
    # Cluster assignment
    cluster = models.IntegerField(
        verbose_name="Cluster",
        help_text="Assigned cluster number (0-3)"
    )
    
    # Optional metadata
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Institution Name",
        help_text="Optional name for the institution"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"
    
    def __str__(self):
        if self.name:
            return f"{self.name} (Cluster {self.cluster})"
        return f"Institution #{self.id} (Cluster {self.cluster})"
    
    def get_cluster_name(self):
        """Return human-readable cluster name."""
        cluster_names = {
            0: "Small Metropolitan Schools",
            1: "Medium-to-Large Institutions",
            2: "Standard Small Schools",
            3: "Overseas Territories"
        }
        return cluster_names.get(self.cluster, f"Cluster {self.cluster}")
    
    @property
    def total_students(self):
        """Calculate total number of students."""
        return self.eleves_premier + self.eleves_superieur
 
