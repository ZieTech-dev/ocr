from django import forms
from .models import ImageOCR

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageOCR
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }