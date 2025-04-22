from django.contrib import admin
from .models import ImageOCR

@admin.register(ImageOCR)
class ImageOCRAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'image')
    readonly_fields = ('extracted_text', 'created_at')
    search_fields = ('extracted_text',)
    list_filter = ('created_at',)