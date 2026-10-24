# يشغّل الموقع في الخلفية (بدون نافذة) إذا لم يكن يعمل، ثم يفتحه في المتصفح.
# الاستخدام: powershell -ExecutionPolicy Bypass -File scripts\start_site.ps1 [-NoBrowser]
param([switch]$NoBrowser)

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$logs = Join-Path $root "logs"
$url = "http://127.0.0.1:8000"

function Test-Site {
    try { Invoke-RestMethod "$url/api/health" -TimeoutSec 2 | Out-Null; return $true } catch { return $false }
}

if (-not (Test-Site)) {
    New-Item -ItemType Directory -Force $logs | Out-Null
    Start-Process -FilePath $python -ArgumentList "-m", "smart_flow.web" `
        -WorkingDirectory $root -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logs "server.out.log") `
        -RedirectStandardError (Join-Path $logs "server.err.log")

    # ننتظر حتى 30 ثانية إلى أن يجهز الخادم
    for ($i = 0; $i -lt 60 -and -not (Test-Site); $i++) { Start-Sleep -Milliseconds 500 }
}

if (-not (Test-Site)) {
    Write-Host "The site did not start. See logs\server.err.log"
    exit 1
}

if (-not $NoBrowser) { Start-Process "http://localhost:8000" }
