from django import forms
from .models import CustomUser


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email Address'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-input-file',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['profile_image'].required = False

 
