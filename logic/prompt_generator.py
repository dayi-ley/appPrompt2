import re
from typing import Dict, List, Set

class PromptGenerator:
    """Generador de prompts en tiempo real basado en categorías activas."""
    
    def __init__(self):
        # Orden lógico basado en categories.json
        self.category_order = [
            "angulo",
            "calidad_tecnica", 
            "estilo_artistico",
            "composicion",
            "atmosfera_vibe",
            "loras_estilos_artistico",
            "loras_detalles_mejoras",
            "loras_modelos_especificos",
            "loras_personaje",
            "fondo",
            "personaje",
            "cabello_forma",
            "cabello_color",
            "cabello_accesorios",
            "rostro_accesorios",
            "ojos",
            "expresion_facial_ojos",
            "expresion_facial_mejillas",
            "expresion_facial_boca",
            "postura_cabeza",
            "direccion_mirada_personaje",
            "vestuario_general",
            "vestuario_superior",
            "vestuario_inferior",
            "vestuario_accesorios",
            "ropa_interior_superior",
            "ropa_interior_inferior",
            "ropa_interior_accesorios",
            "tipo_de_cuerpo",
            "rasgo_fisico_cuerpo",
            "rasgo_fisico_piernas",
            "pose_actitud_global",
            "pose_brazos",
            "pose_piernas",
            "orientacion_personaje",
            "actitud_emocion",
            "nsfw",
            "objetos_interaccion",
            "objetos_escenario",
            "mirada_espectador"
        ]
        
        # Diccionario para almacenar las categorías activas
        self.active_categories: Dict[str, str] = {}
        
        # Set para detectar términos duplicados
        self.duplicate_terms: Set[str] = set()
        
    def update_category(self, category_name: str, value: str):
        """Actualiza el valor de una categoría."""
        if value and value.strip():
            self.active_categories[category_name] = value.strip()
        else:
            self.active_categories.pop(category_name, None)
    
    def clear_category(self, category_name: str):
        """Limpia una categoría específica."""
        self.active_categories.pop(category_name, None)
    
    def clear_all(self):
        """Limpia todas las categorías."""
        self.active_categories.clear()
    
    def validate_input(self, text: str) -> str:
        """Valida y limpia el input del usuario."""
        if not text:
            return ""
        
        # Limpiar espacios extra
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Permitir paréntesis, corchetes, símbolos comunes en prompts y caracteres especiales
        cleaned = re.sub(r'[^a-zA-Z0-9\s,.()\[\]<>:_-]', '', cleaned)
        
        return cleaned
    
    def remove_duplicates(self, prompt_parts: List[str]) -> List[str]:
        """Elimina términos duplicados del prompt."""
        seen = set()
        unique_parts = []
        
        for part in prompt_parts:
            # Normalizar el término para comparación
            normalized = part.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_parts.append(part)
        
        return unique_parts
    
    def generate_prompt(self) -> str:
        """Genera el prompt final combinando todas las categorías activas."""
        if not self.active_categories:
            return ""
        
        prompt_parts = []
        
        # Procesar categorías en el orden lógico
        for category in self.category_order:
            if category in self.active_categories:
                value = self.active_categories[category]
                if value:
                    # Quitar comas al final para evitar dobles comas
                    cleaned_value = value.rstrip(', ').strip()
                    if cleaned_value:
                        prompt_parts.append(cleaned_value)
        
        # Agregar categorías que no están en el orden predefinido
        for category, value in self.active_categories.items():
            if category not in self.category_order and value:
                # Quitar comas al final para evitar dobles comas
                cleaned_value = value.rstrip(', ').strip()
                if cleaned_value:
                    prompt_parts.append(cleaned_value)
        
        # Eliminar duplicados
        unique_parts = self.remove_duplicates(prompt_parts)
        
        # Unir con comas y espacios de forma consistente
        final_prompt = ", ".join(unique_parts)
        
        # Limpiar espacios extra
        final_prompt = re.sub(r'\s+', ' ', final_prompt)
        final_prompt = final_prompt.strip()
        
        return final_prompt
    
    def get_category_value(self, category_name: str) -> str:
        """Obtiene el valor actual de una categoría."""
        return self.active_categories.get(category_name, "")
    
    def get_active_categories(self) -> Dict[str, str]:
        """Obtiene todas las categorías activas."""
        return self.active_categories.copy()
    
    def get_prompt_statistics(self) -> Dict[str, int]:
        """Obtiene estadísticas del prompt generado."""
        prompt = self.generate_prompt()
        if not prompt:
            return {"total_terms": 0, "total_characters": 0}
        
        terms = [term.strip() for term in prompt.split(",")]
        return {
            "total_terms": len(terms),
            "total_characters": len(prompt)
        }