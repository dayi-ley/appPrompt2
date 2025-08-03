import json
import os
import re
import shutil  # ← AGREGAR ESTE IMPORT
from typing import Dict, Any
from datetime import datetime  # ← AGREGAR ESTE IMPORT

class PresetsManager:
    """Gestor de presets organizados por categorías"""
    
    def __init__(self):
        current_dir = os.path.dirname(os.path.dirname(__file__))
        self.presets_dir = os.path.join(current_dir, "data", "presets")
        self.ensure_base_directory()  # ← Cambiar nombre del método
    
    def ensure_base_directory(self):
        """Asegura que existe el directorio base de presets"""
        # Solo crear el directorio base, no las subcarpetas
        os.makedirs(self.presets_dir, exist_ok=True)
        # Eliminar completamente cualquier creación automática de carpetas
    
    # Eliminar completamente este método comentado
    # def ensure_presets_structure(self):
    #     """Asegura que existe la estructura de carpetas de presets"""
    #     categories = ["vestuarios", "expresiones", "poses", "iluminacion", "angulos"]
    #     
    #     for category in categories:
    #         category_dir = os.path.join(self.presets_dir, category)
    #         os.makedirs(category_dir, exist_ok=True)
    #         
    #         # Crear archivo de ejemplo si no existe
    #         example_file = os.path.join(category_dir, "ejemplos.json")
    #         if not os.path.exists(example_file):
    #             self.create_example_preset(category, example_file)
    
    def create_example_preset(self, category, file_path):
        """Crea un preset de ejemplo para cada categoría"""
        examples = {
            "vestuarios": {
                "presets": {
                    "uniforme_escolar": {
                        "name": "Uniforme Escolar",
                        "description": "Uniforme escolar clásico",
                        "categories": {
                            "Vestuario general": "school uniform",
                            "Vestuario superior": "white shirt, blazer",
                            "Vestuario inferior": "pleated skirt"
                        }
                    }
                }
            },
            "expresiones": {
                "presets": {
                    "sonrisa_dulce": {
                        "name": "Sonrisa Dulce",
                        "description": "Expresión tierna y amigable",
                        "categories": {
                            "Expresión": "sweet smile, gentle expression",
                            "Ojos": "bright eyes, sparkling"
                        }
                    }
                }
            }
            # ... más ejemplos para otras categorías
        }
        
        example_data = examples.get(category, {"presets": {}})
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(example_data, f, indent=2, ensure_ascii=False)
    
    def get_presets_by_category(self, category_id: str) -> Dict[str, Any]:
        """Obtiene todos los presets de una categoría"""
        category_dir = os.path.join(self.presets_dir, category_id)
        all_presets = {}
        
        if os.path.exists(category_dir):
            for file_name in os.listdir(category_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(category_dir, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            presets = data.get('presets', {})
                            all_presets.update(presets)
                    except Exception as e:
                        print(f"Error cargando {file_path}: {e}")
        
        return all_presets
    
    def save_preset(self, preset_type, preset_name, preset_data):
        """Guarda un preset con las categorías seleccionadas y las imágenes"""
        # Crear directorio si no existe
        category_dir = os.path.join(self.presets_dir, preset_type)
        os.makedirs(category_dir, exist_ok=True)
        
        # Generar nombre de archivo seguro
        safe_filename = re.sub(r'[^\w\s-]', '', preset_name).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename).lower()
        
        # Crear carpeta de imágenes si hay imágenes
        images_data = []
        if preset_data.get('images'):
            images_dir = os.path.join(category_dir, f"{safe_filename}_images")
            os.makedirs(images_dir, exist_ok=True)
            
            for i, image_path in enumerate(preset_data['images']):
                if os.path.exists(image_path):
                    # Copiar imagen a la carpeta del preset
                    import shutil
                    file_extension = os.path.splitext(image_path)[1]
                    new_image_name = f"image_{i+1}{file_extension}"
                    new_image_path = os.path.join(images_dir, new_image_name)
                    shutil.copy2(image_path, new_image_path)
                    images_data.append(new_image_name)
        
        # Crear estructura del preset
        preset_structure = {
            "presets": {
                safe_filename: {
                    "name": preset_name,
                    "categories": preset_data['categories'],
                    "images": images_data,
                    "created_at": preset_data.get('created_at', datetime.now().isoformat())
                }
            }
        }
        
        # Guardar archivo JSON
        file_path = os.path.join(category_dir, f"{safe_filename}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(preset_structure, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_all_preset_folders(self):
        """Obtiene todas las carpetas de presets (solo personalizadas)"""
        # Solo buscar carpetas personalizadas que realmente existen
        custom_folders = {}
        if os.path.exists(self.presets_dir):
            for item in os.listdir(self.presets_dir):
                item_path = os.path.join(self.presets_dir, item)
                if os.path.isdir(item_path):
                    # Todas las carpetas son personalizadas ahora
                    display_name = item.replace('_', ' ').title()
                    custom_folders[item] = {
                        "display_name": f"📂 {display_name}",
                        "is_custom": True
                    }
    
        return custom_folders
    
    def create_custom_folder(self, folder_name):
        """Crea una nueva carpeta personalizada de presets"""
        try:
            # Convertir nombre a formato de carpeta (sin espacios, minúsculas)
            folder_id = self.sanitize_folder_name(folder_name)
            folder_path = os.path.join(self.presets_dir, folder_id)
            
            # Verificar que no exista
            if os.path.exists(folder_path):
                return False
            
            # Crear la carpeta
            os.makedirs(folder_path, exist_ok=True)
            
            # NO crear archivo de información automáticamente
            # Solo crear la carpeta vacía
            
            return True
            
        except Exception as e:
            print(f"Error creando carpeta personalizada: {e}")
            return False
    
    def sanitize_folder_name(self, name):
        """Convierte un nombre de carpeta a formato válido para sistema de archivos"""
        # Convertir a minúsculas y reemplazar espacios con guiones bajos
        sanitized = name.lower().strip()
        sanitized = re.sub(r'[^a-z0-9\s\-_]', '', sanitized)  # Solo letras, números, espacios, guiones
        sanitized = re.sub(r'\s+', '_', sanitized)  # Espacios a guiones bajos
        sanitized = re.sub(r'_+', '_', sanitized)  # Múltiples guiones bajos a uno solo
        return sanitized.strip('_')  # Quitar guiones bajos al inicio/final
    
    def load_preset(self, preset_type, preset_name):
        """Carga un preset específico"""
        # Generar nombre de archivo seguro
        safe_filename = re.sub(r'[^\w\s-]', '', preset_name).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename).lower()
        
        file_path = os.path.join(self.presets_dir, preset_type, f"{safe_filename}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            preset_data = data.get('presets', {}).get(safe_filename, {})
            
            # Cargar rutas completas de imágenes
            if preset_data.get('images'):
                images_dir = os.path.join(self.presets_dir, preset_type, f"{safe_filename}_images")
                full_image_paths = []
                for image_name in preset_data['images']:
                    full_path = os.path.join(images_dir, image_name)
                    if os.path.exists(full_path):
                        full_image_paths.append(full_path)
                preset_data['images'] = full_image_paths
                
            return preset_data
            
        except Exception as e:
            print(f"Error al cargar preset: {e}")
            return None