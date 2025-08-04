@echo off
echo Backing up current admin_benutzer.html file...
copy "c:\Users\zakar\ProjektmanagementDHBW\backend\templates\admin_benutzer.html" "c:\Users\zakar\ProjektmanagementDHBW\backend\templates\admin_benutzer.html.bak"

echo Deploying new admin_benutzer.html file...
copy "c:\Users\zakar\ProjektmanagementDHBW\backend\templates\admin_benutzer_new.html" "c:\Users\zakar\ProjektmanagementDHBW\backend\templates\admin_benutzer.html"

echo Done!
echo.
echo You can now start the backend server with the start.ps1 script.
echo.
pause
