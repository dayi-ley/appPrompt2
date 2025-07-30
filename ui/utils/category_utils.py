import os
import json

# Constantes de rutas
CATEGORIES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "categories.json")
TAGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "tags.json")
ICON_EDIT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "edit.png")
ICON_SAVE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons", "save.png")

# Constantes de estilo
DEFAULT_CARD_COLOR = "#252525"

def load_categories_and_tags():
    """Carga las categorías y sus tags asociados desde los archivos JSON"""
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        categories = json.load(f)["categorias"]
    with open(TAGS_PATH, "r", encoding="utf-8") as f:
        tags = json.load(f)
    # Relaciona cada categoría con sus tags (o lista vacía si no hay)
    categories_real = [
        {"name": cat.replace("_", " ").capitalize(), "icon": None, "tags": tags.get(cat, [])}
        for cat in categories
    ]
    return categories_real

def normalize_category(name):
    """Normaliza el nombre de una categoría para búsquedas"""
    return name.lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "")

def update_categories_json(name):
    """Actualiza el archivo categories.json con una nueva categoría"""
    with open(CATEGORIES_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        if name not in data["categorias"]:
            data["categorias"].append(name)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
            return True
    return False

def update_tags_json(name, tags):
    """Actualiza el archivo tags.json con los tags de una categoría"""
    with open(TAGS_PATH, "r+", encoding="utf-8") as f:
        tags_data = json.load(f)
        tags_data[name] = tags
        f.seek(0)
        json.dump(tags_data, f, ensure_ascii=False, indent=2)
        f.truncate()

def rename_category_in_files(old_name, new_name):
    """Renombra una categoría en todos los archivos JSON"""
    # Actualizar categories.json
    with open(CATEGORIES_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        if old_name in data["categorias"]:
            index = data["categorias"].index(old_name)
            data["categorias"][index] = new_name
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
    
    # Actualizar tags.json
    old_key = old_name.lower().replace(" ", "_")
    new_key = new_name.lower().replace(" ", "_")
    
    with open(TAGS_PATH, "r+", encoding="utf-8") as f:
        tags_data = json.load(f)
        if old_key in tags_data:
            tags_data[new_key] = tags_data.pop(old_key)
            f.seek(0)
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
            f.truncate()