[app]
title = HealthMate
package.name = healthmate
package.domain = org.healthmate
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json
version = 1.0
requirements = python3==3.11.6,kivy==2.3.0,requests,certifi

orientation = portrait
fullscreen = 1

android.permissions = INTERNET,ACCESS_FINE_LOCATION,VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

android.presplash_color = #1A2535

[buildozer]
log_level = 2
warn_on_root = 1
