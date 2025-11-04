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
requirements = python3==3.9.17,hostpython3==3.9.17,kivy==2.2.1,pillow,yt-dlp,ffpyplayer,android

# Android specific settings
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.gradle_dependencies = org.videolan.android:libvlc-all:3.5.1
android.accept_sdk_license = True
android.arch = arm64-v8a

# Build settings
android.enable_androidx = True
android.add_dependencies = ffmpeg-android
android.add_aars = libs/*.aar
android.add_jars = libs/*.jar

# Application class name and build tools
android.gradle_version = 7.6.1
android.build_tools_version = 33.0.2
# Removing incorrect meta_data line as it's not needed for basic functionality

[buildozer]
# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Window to build for
warn_on_root = 1