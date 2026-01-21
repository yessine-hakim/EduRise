from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Custom user model with roles and additional fields"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('INSTITUTION_MANAGER', 'Institution Manager'),
        ('SERVICE_MANAGER', 'Service Manager'),
    ]
    
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='INSTITUTION_MANAGER',
        help_text='User role determines access permissions'
    )
    
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        help_text='Optional profile picture'
    )
    
    email = models.EmailField(unique=True, blank=False)
    
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'ADMIN'
    
    def is_institution_manager(self):
        """Check if user is an institution manager"""
        return self.role == 'INSTITUTION_MANAGER'
    
    def is_service_manager(self):
        """Check if user is a service manager"""
        return self.role == 'SERVICE_MANAGER'
    
    def get_accessible_sections(self):
        """Return list of sections accessible to this user role"""
        if self.is_admin():
            return ['overview', 'dashboard', 'institutions', 'enrollment', 'services', 'ulis']
        elif self.is_institution_manager():
            return ['overview', 'institutions', 'enrollment']
        elif self.is_service_manager():
            return ['overview', 'services', 'ulis']
        return ['overview']
 
