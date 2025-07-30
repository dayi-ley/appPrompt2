import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class VariationsManager:
    """Gestor de variaciones de prompts para personajes"""
    
    def __init__(self, variations_file: str = None):
        if variations_file is None:
            # Obtener la ruta del archivo de variaciones
            current_dir = os.path.dirname(os.path.dirname(__file__))
            self.variations_file = os.path.join(current_dir, "data", "variations.json")
        else:
            self.variations_file = variations_file
        
        self.ensure_variations_file()
    
    def ensure_variations_file(self):
        """Asegura que el archivo de variaciones existe"""
        if not os.path.exists(self.variations_file):
            os.makedirs(os.path.dirname(self.variations_file), exist_ok=True)
            # Crear estructura inicial
            initial_data = {
                "characters": {},
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            }
            self.save_variations_data(initial_data)
    
    def load_variations_data(self) -> Dict[str, Any]:
        """Carga los datos de variaciones desde el archivo"""
        try:
            with open(self.variations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_variations_file()
            return self.load_variations_data()
    
    def save_variations_data(self, data: Dict[str, Any]):
        """Guarda los datos de variaciones al archivo"""
        data["metadata"]["last_modified"] = datetime.now().isoformat()
        with open(self.variations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_character_variations(self, character_name: str) -> Dict[str, Any]:
        """Obtiene todas las variaciones de un personaje"""
        data = self.load_variations_data()
        return data["characters"].get(character_name, {})
    
    def get_character_base_config(self, character_name: str) -> Dict[str, Any]:
        """Obtiene la configuración base de un personaje"""
        character_data = self.get_character_variations(character_name)
        return character_data.get("base_config", {})
    
    def save_variation(self, character_name: str, variation_name: str, 
                      categories: Dict[str, str], description: str = "",
                      tags: List[str] = None, notes: str = "",
                      inherit_from: str = None) -> bool:
        """Guarda una nueva variación para un personaje"""
        try:
            data = self.load_variations_data()
            
            # Asegurar que el personaje existe
            if character_name not in data["characters"]:
                data["characters"][character_name] = {
                    "base_config": {},
                    "variations": {}
                }
            
            # Crear la variación
            variation_data = {
                "name": variation_name,
                "description": description,
                "tags": tags or [],
                "categories": categories,
                "created_date": datetime.now().isoformat(),
                "rating": 0,
                "notes": notes
            }
            
            if inherit_from:
                variation_data["inherit_from"] = inherit_from
            
            # Guardar la variación
            data["characters"][character_name]["variations"][variation_name] = variation_data
            
            self.save_variations_data(data)
            return True
            
        except Exception as e:
            print(f"Error al guardar variación: {e}")
            return False
    
    def load_variation(self, character_name: str, variation_name: str) -> Optional[Dict[str, Any]]:
        """Carga una variación específica"""
        character_data = self.get_character_variations(character_name)
        variations = character_data.get("variations", {})
        
        if variation_name not in variations:
            return None
        
        variation = variations[variation_name].copy()
        
        # Si hereda de otra variación, combinar las categorías
        if "inherit_from" in variation:
            parent_variation = variations.get(variation["inherit_from"])
            if parent_variation:
                # Combinar categorías (la variación actual sobrescribe la padre)
                combined_categories = parent_variation.get("categories", {}).copy()
                combined_categories.update(variation.get("categories", {}))
                variation["categories"] = combined_categories
        
        return variation
    
    def copy_variation_to_character(self, source_char: str, source_variation: str,
                                   target_char: str, new_variation_name: str = None) -> bool:
        """Copia una variación de un personaje a otro"""
        try:
            # Cargar la variación fuente
            source_variation_data = self.load_variation(source_char, source_variation)
            if not source_variation_data:
                return False
            
            # Nombre de la nueva variación
            if not new_variation_name:
                new_variation_name = f"{source_variation}_copy"
            
            # Guardar en el personaje destino
            return self.save_variation(
                target_char,
                new_variation_name,
                source_variation_data.get("categories", {}),
                f"Copiado de {source_char}: {source_variation_data.get('description', '')}",
                source_variation_data.get("tags", []),
                source_variation_data.get("notes", "")
            )
            
        except Exception as e:
            print(f"Error al copiar variación: {e}")
            return False
    
    def delete_variation(self, character_name: str, variation_name: str) -> bool:
        """Elimina una variación"""
        try:
            data = self.load_variations_data()
            
            if (character_name in data["characters"] and 
                "variations" in data["characters"][character_name] and
                variation_name in data["characters"][character_name]["variations"]):
                
                del data["characters"][character_name]["variations"][variation_name]
                self.save_variations_data(data)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error al eliminar variación: {e}")
            return False
    
    def get_variation_info(self, character_name: str, variation_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información completa de una variación"""
        variation = self.load_variation(character_name, variation_name)
        if variation:
            variation["character"] = character_name
        return variation
    
    def search_variations_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Busca variaciones por etiqueta"""
        results = []
        data = self.load_variations_data()
        
        for char_name, char_data in data["characters"].items():
            variations = char_data.get("variations", {})
            for var_name, var_data in variations.items():
                if tag.lower() in [t.lower() for t in var_data.get("tags", [])]:
                    result = var_data.copy()
                    result["character"] = char_name
                    result["variation_name"] = var_name
                    results.append(result)
        
        return results
    
    def get_all_characters_with_variations(self) -> List[str]:
        """Obtiene lista de todos los personajes que tienen variaciones"""
        data = self.load_variations_data()
        return list(data["characters"].keys())
    
    def export_variation(self, character_name: str, variation_name: str, 
                        export_path: str) -> bool:
        """Exporta una variación a un archivo JSON"""
        try:
            variation_data = self.get_variation_info(character_name, variation_name)
            if not variation_data:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(variation_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error al exportar variación: {e}")
            return False
    
    def update_base_config(self, character_name: str, categories: Dict[str, str]):
        """Actualiza la configuración base de un personaje"""
        try:
            data = self.load_variations_data()
            
            if character_name not in data["characters"]:
                data["characters"][character_name] = {
                    "base_config": {},
                    "variations": {}
                }
            
            data["characters"][character_name]["base_config"] = categories
            self.save_variations_data(data)
            
        except Exception as e:
            print(f"Error al actualizar configuración base: {e}")