from django.db import models
import cv2
import numpy as np
import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract


class ImageOCR(models.Model):
    image = models.ImageField(upload_to='images/')
    extracted_text = models.TextField(blank=True, null=True)
    structured_data = models.JSONField(blank=True, null=True)  # Nouveau champ
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OCR Image {self.id} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']


class IDCardProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.text_data = {}
        
    def preprocess_image(self, image):
        """Prétraitement avancé de l'image"""
        # Convertir en numpy array
        img_array = np.array(image)
        
        # Convertir en niveaux de gris
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Augmenter le contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(gray)
        
        # Appliquer un flou gaussien pour réduire le bruit
        blurred = cv2.GaussianBlur(contrast, (3, 3), 0)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Débruitage
        denoised = cv2.fastNlMeansDenoising(binary)
        
        # Convertir en PIL Image
        return Image.fromarray(denoised)
    
    def extract_zones(self, image):
        """Détection des zones de texte"""
        img_array = np.array(image)
        
        # Détection des contours
        edges = cv2.Canny(img_array, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        zones = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 30 and h > 10:  # Filtrer les petits contours
                zones.append((x, y, w, h))
        
        return zones
    
    def parse_text(self, text):
        """Parser le texte extrait pour identifier les champs"""
        lines = text.split('\n')
        data = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Chercher le numéro de carte
            if 'C100' in line or 'n°' in line:
                match = re.search(r'C\d{10}', line)
                if match:
                    data['numero_carte'] = match.group()
            
            # Chercher le nom
            if i > 0 and 'Nom' in lines[i-1]:
                data['nom'] = line
            
            # Chercher les prénoms
            if 'Prénom' in line:
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                data['prenom'] = next_line
            
            # Chercher la date de naissance
            if 'naissance' in line.lower():
                match = re.search(r'\d{2}/\d{2}/\d{4}', line)
                if match:
                    data['date_naissance'] = match.group()
                else:
                    # Chercher sur la ligne suivante
                    if i+1 < len(lines):
                        match = re.search(r'\d{2}/\d{2}/\d{4}', lines[i+1])
                        if match:
                            data['date_naissance'] = match.group()
            
            # Chercher le sexe
            if 'Sexe' in line:
                if 'M' in line.upper():
                    data['sexe'] = 'M'
                elif 'F' in line.upper():
                    data['sexe'] = 'F'
            
            # Chercher la taille
            if 'Taille' in line:
                match = re.search(r'\d,\d{2}', line)
                if match:
                    data['taille'] = match.group()
            
            # Chercher la nationalité
            if 'Nationalité' in line or 'IVOIRIENNE' in line:
                data['nationalite'] = 'IVOIRIENNE'
            
            # Chercher la date d'expiration
            if i > 0 and any(exp in lines[i-1] for exp in ['Expiration', 'Expire', 'Valid']):
                match = re.search(r'\d{2}/\d{2}/\d{4}', line)
                if match:
                    data['date_expiration'] = match.group()
        
        return data
    
    def process(self):
        """Processus complet"""
        # Ouvrir l'image
        image = Image.open(self.image_path)
        
        # Prétraitement
        processed_image = self.preprocess_image(image)
        
        # Extraction complète du texte
        custom_config = r'--oem 3 --psm 6'
        full_text = pytesseract.image_to_string(processed_image, lang='fra', config=custom_config)
        
        # Essayer aussi avec d'autres modes
        try:
            # Mode 3: Segmentation automatique
            config_auto = r'--oem 3 --psm 3'
            text_auto = pytesseract.image_to_string(processed_image, lang='fra', config=config_auto)
            
            # Mode 4: Texte sur une seule colonne
            config_single = r'--oem 3 --psm 4'
            text_single = pytesseract.image_to_string(processed_image, lang='fra', config=config_single)
            
            # Combiner les résultats
            all_text = full_text + "\n" + text_auto + "\n" + text_single
            
        except Exception as e:
            all_text = full_text
        
        # Parser le texte
        self.text_data = self.parse_text(all_text)
        
        return self.text_data, full_text