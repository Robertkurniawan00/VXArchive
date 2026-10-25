@echo off
title Remove VXArchive System Integration
cls
echo =====================================================================
echo   VXArchive - Remove System Associations & Context Menus
echo =====================================================================
echo.
echo Removing HKCU file associations and context menu hooks...
python -c "from vxarchive.core.shell_integration import ShellIntegration; ok, msg = ShellIntegration.unregister_associations(); print('[OK] ' + msg)"
echo.
echo Done! Associations removed cleanly.
echo.
pause
