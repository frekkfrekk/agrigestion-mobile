[app]
# --- Identité de l'app ---
title = AgriGestion
package.name = agrigestion
package.domain = org.agrigestion

# --- Source ---
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# --- Version ---
version = 3.4

# --- Dépendances Python ---
requirements = python3,kivy==2.2.1

# --- Affichage ---
orientation = portrait
fullscreen = 0

# --- Android : SPÉCIALISÉ SAMSUNG (arm64-v8a uniquement) ---
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 24
android.ndk = 25b

# ⚡ UNE SEULE architecture = compil rapide + pas d'OOM
android.archs = arm64-v8a

android.allow_backup = True
android.accept_sdk_license = True

# --- python-for-android (fork officiel Kivy) ---
p4a.branch = master
p4a.fork = kivy

# --- Optimisations ---
p4a.extra_args = --no-byte-compile-python

# --- Buildozer ---
[buildozer]
log_level = 2
warn_on_root = 1
