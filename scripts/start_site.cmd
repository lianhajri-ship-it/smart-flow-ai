@echo off
rem Double-click to start the site and open it in the browser.
rem Add -NoBrowser to only start it in the background (useful for auto-start).
powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0start_site.ps1" %*
