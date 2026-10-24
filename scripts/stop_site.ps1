# يوقف الموقع الذي يعمل في الخلفية على المنفذ 8000.
# الاستخدام: powershell -ExecutionPolicy Bypass -File scripts\stop_site.ps1

$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $connections) {
    Write-Host "The site is not running."
    exit 0
}

foreach ($id in ($connections.OwningProcess | Sort-Object -Unique)) {
    Stop-Process -Id $id -Force
}
Write-Host "The site has been stopped."
