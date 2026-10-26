@echo off
if exist "%~dp0dist\VXArchive\VXArchive.exe" (
    start "" "%~dp0dist\VXArchive\VXArchive.exe" %*
) else (
    start "" pythonw "%~dp0vxarchive\main.py" %*
)
