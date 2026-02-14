@echo off
REM YOLOP Workflow Helper - Windows Batch Script
REM This script helps you prepare videos and test YOLOP workflow
REM Note: Actual YOLOP processing runs on Jetson Nano (this is a helper)

setlocal enabledelayedexpansion

echo ========================================
echo YOLOP Jetson Nano Workflow Helper
echo ========================================
echo.

:menu
echo.
echo Options:
echo 1. Create directory structure
echo 2. Check workflow files
echo 3. Show video instructions
echo 4. Show workflow documentation
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto create_dirs
if "%choice%"=="2" goto check_files
if "%choice%"=="3" goto video_instructions
if "%choice%"=="4" goto show_docs
if "%choice%"=="5" goto end
echo Invalid choice. Try again.
goto menu

:create_dirs
echo.
echo Creating directory structure...
if not exist "videos\input" mkdir videos\input && echo Created: videos\input
if not exist "videos\output" mkdir videos\output && echo Created: videos\output
if not exist "weights" mkdir weights && echo Created: weights
echo.
echo Directories ready! Copy your .mp4 files to: videos\input\
goto menu

:check_files
echo.
echo Checking workflow files...
echo.
for %%F in (
    "process_video_jetson.py"
    "quick_process.py"
    "batch_process_videos.py"
    "setup_jetson_nano.sh"
    "JETSON_NANO_WORKFLOW.md"
    "QUICKSTART.md"
) do (
    if exist "%%~F" (
        echo [OK] %%~F
    ) else (
        echo [MISSING] %%~F
    )
)
echo.
goto menu

:video_instructions
echo.
echo ===== VIDEO PREPARATION =====
echo.
echo 1. Place your .mp4 files in: videos\input\
echo.
echo    Example:
echo    - videos\input\highway_drive.mp4
echo    - videos\input\parking_lot.mp4
echo    - videos\input\street_scene.mp4
echo.
echo 2. File naming (input):
echo    - Name: any_name.mp4
echo    - Only supported format: MP4
echo    - Recommended: Use video editing software to adjust resolution/codec
echo.
echo 3. Expected output (on Jetson):
echo    - Name: detected_any_name.mp4
echo    - Location: videos\output\ (on Jetson Nano)
echo    - Format: Same as input
echo.
echo ===== TRANSFER TO JETSON =====
echo.
echo After processing on Jetson Nano:
echo 1. Connect to Jetson via SCP/WinSCP
echo 2. Download from: /path/to/YOLOP/videos/output/detected_*.mp4
echo 3. Results ready for use!
echo.
goto menu

:show_docs
echo.
echo Available Documentation:
echo.
echo 1. QUICKSTART.md - Fast 60-second setup guide
echo 2. JETSON_NANO_WORKFLOW.md - Complete reference guide
echo 3. README_SUMMARY.txt - Overview of workflow
echo.
echo Open these files in a text editor (Notepad, VSCode, etc.)
echo Or on Jetson Nano with: cat QUICKSTART.md
echo.
goto menu

:end
echo.
echo Thank you! Start with QUICKSTART.md on your Jetson Nano.
echo.
pause
