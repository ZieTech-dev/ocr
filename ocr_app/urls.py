from django.urls import path
from . import views

app_name = 'ocr_app'

urlpatterns = [
    path('', views.ImageUploadView.as_view(), name='upload'),
    path('result/<int:pk>/', views.OCRResultView.as_view(), name='result'),
]