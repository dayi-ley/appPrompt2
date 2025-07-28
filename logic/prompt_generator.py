import re
from typing import Dict, List, Set

class PromptGenerator:
    """Generador de prompts en tiempo real basado en categorías activas."""
    
    def __init__(self):
        # Orden lógico para las categorías
        self.category_order = [
            "Calidad técnica",
            "Estilo artístico", 
            "LORAS",
            "Ángulo",
            "Composición",
            "Atmósfera",
            "Fondo",
            "Cabello",
            "Ropa",
            "Poses",
            "Expresión facial",
            "Orientación",
            "Interacciones",
            "Iluminación",
            "Color",
            "Textura",
            "Accesorios",
            "Emociones",
            "Acción",
            "Perspectiva",
            "Profundidad",
            "Tiempo",
            "Clima",
            "Estación",
            "Edad",
            "Género",
            "Cultura",
            "Profesión",
            "Fantasy",
            "Tecnología",
            "Arquitectura",
            "Naturaleza",
            "Materiales",
            "Patrones",
            "Movimiento",
            "Sonido",
            "Temperatura",
            "Humedad",
            "Viento",
            "Reflejos",
            "Sombras",
            "Contraste",
            "Saturación",
            "NSFW"
        ]
        
        # Categorías activas y sus valores
        self.active_categories: Dict[str, str] = {}
        
        # Términos duplicados detectados
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
        
        # Remover caracteres problemáticos (mantener solo letras, números, espacios, comas, puntos, guiones)
        cleaned = re.sub(r'[^a-zA-Z0-9\s,.-]', '', cleaned)
        
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
                    prompt_parts.append(value)
        
        # Agregar categorías que no están en el orden predefinido
        for category, value in self.active_categories.items():
            if category not in self.category_order and value:
                prompt_parts.append(value)
        
        # Eliminar duplicados
        unique_parts = self.remove_duplicates(prompt_parts)
        
        # Unir con comas
        final_prompt = ", ".join(unique_parts)
        
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