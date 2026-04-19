[app]
title = HealthMate
package.name = healthmate
package.domain = org.healthmate

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 1.0

# 🔥 СТАБИЛЬНАЯ связка
requirements = python3,kivy==2.2.1,requests,certifi

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_FINE_LOCATION,VIBRATE

android.api = 33
android.minapi = 21

android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

icon.filename = %(source.dir)s/images/logo.png
presplash.filename = %(source.dir)s/images/background.png

[buildozer]
log_level = 2
warn_on_root = 1
