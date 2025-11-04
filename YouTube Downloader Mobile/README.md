# YouTube Downloader Mobile

A mobile version of YouTube Downloader that works on Android devices.

## Features
- Download YouTube videos or extract audio
- Multiple quality options
- Progress tracking
- Modern mobile-friendly interface

## Installation
1. Install from APK file
2. Grant storage permissions when prompted
3. Start downloading videos!

## Build from Source
To build the APK from source:

1. Install buildozer:
```bash
pip install buildozer
```

2. Initialize buildozer:
```bash
buildozer init
```

3. Build the APK:
```bash
buildozer android debug deploy
```

## Requirements
- Android 5.0 or higher
- Storage permission for saving downloads
- Internet connection

## Notes
- Downloads are saved to the Downloads folder
- Audio extraction requires FFmpeg support
- Not available on iOS