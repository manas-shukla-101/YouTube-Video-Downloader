[app]

# App name and version
title = YouTube Downloader Pro
package.name = youtubedownloader
package.domain = org.youtubedownloader
version = 1.0

# Source code location
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Python requirements
requirements = python3,kivy,yt-dlp,pillow,certifi

# Android specific settings
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = armeabi-v7a

# Build optimizations
android.release_artifact = apk
android.allow_backup = False
android.enable_androidx = True
p4a.bootstrap = sdl2

# APK size optimizations
android.enable_proguard = True
android.minify = True
android.strip = True
android.gradle_dependencies = androidx.multidex:multidex:2.0.1

# FFmpeg minimal configuration
android.add_dependencies = ffmpeg-android-min
p4a.ffmpeg_min = True
ffmpeg.min_size = True

# Enable app bundle and split APKs by ABI
android.enable_bundle = True
android.split_per_abi = True

# Application class name
android.meta_data = org.youtubedownloader.YouTubeDownloaderApp

[buildozer]
# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Window to build for
warn_on_root = 1