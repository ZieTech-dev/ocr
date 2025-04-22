# Créez un fichier test_tesseract.py dans le répertoire racine
import pytesseract
import platform
import os
from PIL import Image

def test_tesseract():
    print("Test de l'installation de Tesseract...")
    
    # Vérifier le système d'exploitation
    system = platform.system()
    print(f"Système d'exploitation: {system}")
    
    # Configurer le chemin pour Windows
    if system == 'Windows':
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tesseract-OCR\tesseract.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"Tesseract trouvé à: {path}")
                break
        else:
            print("Tesseract n'a pas été trouvé aux chemins par défaut")
            print("Veuillez installer Tesseract depuis: https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    
    try:
        # Tester si Tesseract fonctionne
        version = pytesseract.get_tesseract_version()
        print(f"Version de Tesseract: {version}")
        
        # Vérifier les langues disponibles
        langs = pytesseract.get_languages()
        print(f"Langues disponibles: {langs}")
        
        if 'fra' not in langs:
            print("Attention: Le français n'est pas installé!")
            print("Installez le pack de langue française.")
        
        return True
    
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    test_tesseract()