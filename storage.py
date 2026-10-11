"""
Stockage des données pour AgriGestion Mobile.
Utilise le dossier privé de l'app sur Android (via app.user_data_dir).
"""
import json
import os
from kivy.app import App


def _data_file():
    app = App.get_running_app()
    # Sur Android : /data/data/org.agrigestion.agrigestion/files
    # Sur desktop : ~/.agrigestion
    if app is None:
        base = os.path.join(os.path.expanduser("~"), ".agrigestion")
    else:
        base = app.user_data_dir
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "data.json")


def load_data():
    path = _data_file()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"fields": []}


def save_data(data):
    path = _data_file()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
