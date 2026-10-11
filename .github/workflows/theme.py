"""Gestion des thèmes clair / sombre pour AgriGestion Mobile."""

LIGHT = {
    "name": "Clair",
    "bg": (0.96, 0.97, 0.96, 1),
    "card": (1, 1, 1, 1),
    "text": (0.17, 0.24, 0.31, 1),
    "text_muted": (0.5, 0.55, 0.55, 1),
    "text_inverse": (1, 1, 1, 1),
    "primary": (0.153, 0.682, 0.376, 1),
    "secondary": (0.204, 0.596, 0.859, 1),
    "danger": (0.906, 0.298, 0.235, 1),
    "dark": (0.204, 0.286, 0.369, 1),
    "border": (0.88, 0.88, 0.88, 1),
}

DARK = {
    "name": "Sombre",
    "bg": (0.118, 0.118, 0.118, 1),
    "card": (0.176, 0.176, 0.176, 1),
    "text": (0.91, 0.91, 0.91, 1),
    "text_muted": (0.63, 0.63, 0.63, 1),
    "text_inverse": (1, 1, 1, 1),
    "primary": (0.18, 0.8, 0.443, 1),
    "secondary": (0.204, 0.596, 0.859, 1),
    "danger": (0.906, 0.298, 0.235, 1),
    "dark": (0.29, 0.29, 0.29, 1),
    "border": (0.227, 0.227, 0.227, 1),
}

_current = {"theme": LIGHT}


def get_theme():
    return _current["theme"]


def set_theme(name):
    _current["theme"] = DARK if name == "dark" else LIGHT
    return _current["theme"]


def is_dark():
    return _current["theme"]["name"] == "Sombre"
