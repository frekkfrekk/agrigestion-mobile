[app]
title = AgriGestion
package.name = agrigestion
package.domain = org.agrigestion

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 3.4
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
