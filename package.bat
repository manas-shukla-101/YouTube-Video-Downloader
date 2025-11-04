@echo off
echo Packaging YouTube Downloader Pro...

REM Create distribution directory
set DIST_DIR=YouTube Downloader Pro
if exist "%DIST_DIR%" rd /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"

REM Copy executable
copy "dist\YouTube Downloader Pro.exe" "%DIST_DIR%\"

REM Create and copy ffmpeg folder
mkdir "%DIST_DIR%\ffmpeg"
copy "ffmpeg\*.exe" "%DIST_DIR%\ffmpeg\"

REM Copy README
copy "README.md" "%DIST_DIR%\"

echo.
echo Package created successfully!
echo You can find the complete package in the 'YouTube Downloader Pro' folder
echo.
pause