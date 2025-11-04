[app]

# App name and version
title = YouTube Downloader Pro
package.name = youtubedownloader
package.domain = org.youtubedownloader
version = 1.0

# Source code location
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ico

# Application icon
icon.filename = icons/icon.png
presplash.filename = icons/icon.png

# Include necessary files
source.include_patterns = icons/*.png,ffmpeg/*,*.txt

# Python requirements
requirements = python3,\
    kivy==2.2.1,\
    yt-dlp==2023.10.13,\
    pillow==10.0.0,\
    certifi==2023.7.22,\
    urllib3==2.0.7,\
    kivymd==1.1.1,\
    plyer==2.1.0,\
    pyjnius

# Android specific settings
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Architecture support (optimized for modern devices)
android.archs = arm64-v8a

# SDK version settings
android.min_sdk_version = 21
android.target_sdk_version = 33
android.accept_sdk_license = True

# Display and orientation settings
android.orientation = portrait
android.presplash_color = #2E3440
android.fullscreen = 0

# Build optimizations
android.release_artifact = apk
android.allow_backup = True
android.enable_androidx = True
p4a.bootstrap = sdl2

# Performance optimizations
android.enable_proguard = True
android.add_adb_to_path = True
android.extra_manifest_xml = <?xml version="1.0" encoding="utf-8"?><manifest><application android:requestLegacyExternalStorage="true" android:usesCleartextTraffic="true" /></manifest>

# Build performance settings
android.gradle_dependencies = androidx.core:core-ktx:1.7.0
android.enable_androidx = True
log_level = 2

# Build hooks for ffmpeg
android.add_src = ffmpeg

# Enable asset packaging for faster startup
android.enable_asset_packing = True
android.minify = False
android.strip = False

# FFmpeg minimal configuration
android.add_dependencies = ffmpeg-android-min

# Disable app bundle and split APKs for simpler build
android.enable_bundle = False
android.split_per_abi = False

# Application class name
# Removing incorrect meta_data line as it's not needed for basic functionality

[buildozer]
# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Window to build for
warn_on_root = 1