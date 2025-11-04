[app]

# App name and version
title = YouTube Downloader
package.name = youtubedownloader
package.domain = org.youtubedownloader
version = 1.0

# Source code location
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Python requirements
requirements = python3,kivy,yt-dlp,pillow

# Android specific settings
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = arm64-v8a

# FFmpeg dependency
android.enable_androidx = True
android.add_dependencies = ffmpeg-android

# Application class name
# Removing incorrect meta_data line as it's not needed for basic functionality

[buildozer]
# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Window to build for
warn_on_root = 1