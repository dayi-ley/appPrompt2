import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class VariationsManager:
    """Gestor de variaciones de prompts para personajes"""
    
    def __init__(self):
        # Ya no necesitamos un archivo global de variaciones
        current_dir = os.path.dirname(os.path.dirname(__file__))
        self.characters_dir = os.path.join(current_dir, "data", "characters")
    
    def get_character_variations_file(self, character_name: str) -> str:
        """Obtiene la ruta del archivo de variaciones para un personaje específico"""
        character_folder = os.path.join(self.characters_dir, character_name.lower().replace(' ', '_'))
        return os.path.join(character_folder, f"{character_name.lower().replace(' ', '_')}_variations.json")
    
    def ensure_character_variations_file(self, character_name: str):
        """Asegura que el archivo de variaciones del personaje existe"""
        variations_file = self.get_character_variations_file(character_name)
        
        if not os.path.exists(variations_file):
            # Crear estructura inicial para el personaje
            initial_data = {
                "character_name": character_name,
                "variations": {},
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            }
            
            # Asegurar que la carpeta del personaje existe
            os.makedirs(os.path.dirname(variations_file), exist_ok=True)
            
            with open(variations_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def load_character_variations_data(self, character_name: str) -> Dict[str, Any]:
        """Carga los datos de variaciones de un personaje específico"""
        variations_file = self.get_character_variations_file(character_name)
        
        try:
            if os.path.exists(variations_file):
                with open(variations_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            
            # Si no existe el archivo, crear estructura inicial
            self.ensure_character_variations_file(character_name)
            return {
                "character_name": character_name,
                "variations": {},
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            }
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error cargando variaciones para {character_name}: {e}")
            return {
                "character_name": character_name,
                "variations": {},
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            }
    
    def save_character_variations_data(self, character_name: str, data: Dict[str, Any]):
        """Guarda los datos de variaciones de un personaje específico"""
        variations_file = self.get_character_variations_file(character_name)
        
        # Actualizar metadata
        data["metadata"]["last_modified"] = datetime.now().isoformat()
        
        # Asegurar que la carpeta existe
        os.makedirs(os.path.dirname(variations_file), exist_ok=True)
        
        with open(variations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_character_variations(self, character_name: str) -> Dict[str, Any]:
        """Obtiene todas las variaciones de un personaje en el formato esperado por el panel"""
        data = self.load_character_variations_data(character_name)
        return {
            "variations": data.get("variations", {}),
            "metadata": data.get("metadata", {})
        }
    
    def get_character_base_config(self, character_name: str) -> Dict[str, Any]:
        """Obtiene la configuración base de un personaje (no implementado en esta versión)"""
        return {}
    
    def save_variation(self, character_name: str, variation_name: str, 
                      categories: Dict[str, str], description: str = "",
                      tags: List[str] = None, notes: str = "",
                      negative_prompt: str = "",  # ← AGREGAR PARÁMETRO
                      inherit_from: str = None) -> bool:
        """Guarda una nueva variación para un personaje"""
        try:
            data = self.load_character_variations_data(character_name)
            
            # Crear la variación
            variation_data = {
                "name": variation_name,
                "description": description,
                "tags": tags or [],
                "categories": categories,
                "negative_prompt": negative_prompt,  # ← GUARDAR NEGATIVE PROMPT
                "created_date": datetime.now().isoformat(),
                "rating": 0,
                "notes": notes
            }
            
            if inherit_from:
                variation_data["inherit_from"] = inherit_from
            
            # Guardar la variación
            data["variations"][variation_name] = variation_data
            
            self.save_character_variations_data(character_name, data)
            return True
            
        except Exception as e:
            print(f"Error al guardar variación: {e}")
            return False
    
    def load_variation(self, character_name: str, variation_name: str) -> Optional[Dict[str, Any]]:
        """Carga una variación específica"""
        try:
            data = self.load_character_variations_data(character_name)
            variations = data.get("variations", {})
            
            if variation_name in variations:
                return variations[variation_name]
            else:
                print(f"Variación '{variation_name}' no encontrada para {character_name}")
                return None
                
        except Exception as e:
            print(f"Error cargando variación: {e}")
            return None
    
    def copy_variation_to_character(self, source_char: str, source_variation: str,
                                   target_char: str, new_variation_name: str = None) -> bool:
        """Copia una variación de un personaje a otro"""
        try:
            # Cargar variación origen
            source_data = self.load_variation(source_char, source_variation)
            if not source_data:
                return False
            
            # Nombre de la nueva variación
            if not new_variation_name:
                new_variation_name = f"{source_variation}_copy"
            
            # Guardar en el personaje destino
            return self.save_variation(
                target_char,
                new_variation_name,
                source_data.get("categories", {}),
                source_data.get("description", ""),
                source_data.get("tags", []),
                source_data.get("notes", ""),
                f"Copiado de {source_char}:{source_variation}"
            )
            
        except Exception as e:
            print(f"Error copiando variación: {e}")
            return False
    
    def delete_variation(self, character_name: str, variation_name: str) -> bool:
        """Elimina una variación específica"""
        try:
            data = self.load_character_variations_data(character_name)
            variations = data.get("variations", {})
            
            if variation_name in variations:
                del variations[variation_name]
                self.save_character_variations_data(character_name, data)
                return True
            else:
                print(f"Variación '{variation_name}' no encontrada")
                return False
                
        except Exception as e:
            print(f"Error eliminando variación: {e}")
            return False
    
    def get_variation_info(self, character_name: str, variation_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una variación específica"""
        return self.load_variation(character_name, variation_name)
    
    def search_variations_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Busca variaciones por tag en todos los personajes"""
        results = []
        
        try:
            # Buscar en todas las carpetas de personajes
            if os.path.exists(self.characters_dir):
                for character_folder in os.listdir(self.characters_dir):
                    character_path = os.path.join(self.characters_dir, character_folder)
                    if os.path.isdir(character_path):
                        character_name = character_folder
                        variations = self.get_character_variations(character_name)
                        
                        for var_name, var_data in variations.items():
                            if tag in var_data.get("tags", []):
                                results.append({
                                    "character": character_name,
                                    "variation_name": var_name,
                                    "data": var_data
                                })
        except Exception as e:
            print(f"Error buscando por tag: {e}")
        
        return results
    
    def get_all_characters_with_variations(self) -> List[str]:
        """Obtiene lista de todos los personajes que tienen variaciones"""
        characters = []
        
        try:
            if os.path.exists(self.characters_dir):
                for character_folder in os.listdir(self.characters_dir):
                    character_path = os.path.join(self.characters_dir, character_folder)
                    if os.path.isdir(character_path):
                        # CAMBIO: Usar el nombre de la carpeta directamente
                        character_name = character_folder
                        variations_file = self.get_character_variations_file(character_name)
                        
                        # Verificar si tiene variaciones
                        if os.path.exists(variations_file):
                            data = self.load_character_variations_data(character_name)
                            if data.get("variations", {}):
                                # CAMBIO: Usar el character_name del JSON, no el nombre de carpeta
                                actual_character_name = data.get("character_name", character_name)
                                characters.append(actual_character_name)
                                print(f"Personaje encontrado: {actual_character_name} (carpeta: {character_folder})")
        except Exception as e:
            print(f"Error obteniendo personajes: {e}")
        
        return characters
    
    def export_variation(self, character_name: str, variation_name: str, 
                        export_path: str) -> bool:
        """Exporta una variación a un archivo"""
        try:
            variation_data = self.load_variation(character_name, variation_name)
            if not variation_data:
                return False
            
            export_data = {
                "character": character_name,
                "variation_name": variation_name,
                "data": variation_data,
                "exported_date": datetime.now().isoformat()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exportando variación: {e}")
            return False
    
    def update_base_config(self, character_name: str, categories: Dict[str, str]):
        """Actualiza la configuración base de un personaje (no implementado en esta versión)"""
        try:
            # Esta funcionalidad se puede implementar más adelante si es necesaria
            print(f"Actualización de configuración base para {character_name} - No implementado")
        except Exception as e:
            print(f"Error al actualizar configuración base: {e}")