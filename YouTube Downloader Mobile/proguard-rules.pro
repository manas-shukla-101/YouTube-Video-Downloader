# Optimize and shrink code
-optimizations !code/simplification/arithmetic,!code/simplification/cast,!field/*,!class/merging/*
-optimizationpasses 5
-allowaccessmodification

# Keep Python classes
-keep public class org.python.** { *; }
-keep public class com.chaquo.python.** { *; }

# Keep Kivy classes
-keep public class org.kivy.** { *; }
-keep public class org.libsdl.** { *; }

# Keep FFmpeg classes
-keep class com.arthenica.ffmpegkit.** { *; }

# Keep yt-dlp related classes
-keep class com.github.ytdl.** { *; }

# Don't warn about missing classes from optional dependencies
-dontwarn org.python.**
-dontwarn org.libsdl.**
-dontwarn org.kivy.**

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep app components
-keep public class org.youtubedownloader.** { *; }