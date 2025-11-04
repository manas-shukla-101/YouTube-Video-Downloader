@echo off
echo Building YouTube Downloader Pro...

REM Create build and dist directories if they don't exist
if not exist "build" mkdir build
if not exist "dist" mkdir dist

REM Install required packages if not already installed
pip install pyinstaller
pip install -r requirements.txt

REM Build the executable
pyinstaller --onefile --noconsole ^
    --name "YouTube Downloader Pro" ^
    --add-data "ffmpeg;ffmpeg" ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    youtube_downloader.py

echo.
echo Build complete! Check the dist folder for your executable.
echo.
pause