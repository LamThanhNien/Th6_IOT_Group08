# Smart Classroom AIoT - System Runner
# Chay toan bo he thong va dung sach se khi nhan Ctrl + C

param(
    [switch]$Simulator
)

$ErrorActionPreference = "Continue"

try {
    $Host.UI.RawUI.WindowTitle = "Smart Classroom AIoT - Dang khoi dong..."
} catch {}

$projectRoot = $PSScriptRoot

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       SMART CLASSROOM AIoT - KHOI DONG HE THONG" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$infraDir   = Join-Path $projectRoot "infrastructure"
$backendDir = Join-Path $projectRoot "backend"
$cameraDir  = Join-Path $projectRoot "ai-camera-service"
$webDir     = Join-Path $projectRoot "web-dashboard"
$simDir     = Join-Path $projectRoot "device-simulator"

$backendPy = Join-Path $backendDir "venv\Scripts\python.exe"
$cameraPy  = Join-Path $cameraDir "venv\Scripts\python.exe"
$simPy     = Join-Path $simDir "venv\Scripts\python.exe"

$spawnedPids = [System.Collections.Generic.List[int]]::new()

try {
    # 1. Khoi dong Docker
    Write-Host "[1/4] Dang khoi dong Docker (PostgreSQL & Mosquitto)..." -ForegroundColor Green
    try { docker stop iot_postgres iot_emqx 2>$null | Out-Null } catch {}
    Push-Location $infraDir
    docker compose up -d
    Pop-Location
    Start-Sleep -Seconds 1

    # 2. Khoi dong Backend FastAPI (Port 8000)
    Write-Host "[2/4] Dang khoi dong FastAPI Backend (Port 8000)..." -ForegroundColor Green
    $backendProc = Start-Process -FilePath $backendPy -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" -WorkingDirectory $backendDir -PassThru -WindowStyle Minimized
    if ($backendProc) { $spawnedPids.Add($backendProc.Id) }

    # 3. Khoi dong AI Camera Service (Port 8001)
    Write-Host "[3/4] Dang khoi dong AI Camera Service (Port 8001)..." -ForegroundColor Green
    $cameraProc = Start-Process -FilePath $cameraPy -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8001" -WorkingDirectory $cameraDir -PassThru -WindowStyle Minimized
    if ($cameraProc) { $spawnedPids.Add($cameraProc.Id) }

    # 4. Khoi dong Web Dashboard ReactJS (Port 5173)
    Write-Host "[4/4] Dang khoi dong Web Dashboard ReactJS (Port 5173)..." -ForegroundColor Green
    $webProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm", "run", "dev" -WorkingDirectory $webDir -PassThru -WindowStyle Minimized
    if ($webProc) { $spawnedPids.Add($webProc.Id) }

    # 5. Tuy chon bat Simulator (Dung cho nguoi dung tu go lua chon)
    Write-Host ""
    Write-Host "----------------------------------------------------------------" -ForegroundColor DarkGray
    $simChoice = Read-Host "Ban co muon bat gia lap ESP32 (Simulator) khong? [y/N] (Nhan Enter mac dinh la N)"
    
    if ($Simulator -or $simChoice -eq "y" -or $simChoice -eq "Y") {
        Write-Host "  -> Dang bat ESP32 Simulator..." -ForegroundColor Cyan
        $simProc = Start-Process -FilePath $simPy -ArgumentList "src\main.py" -WorkingDirectory $simDir -PassThru -WindowStyle Minimized
        if ($simProc) { $spawnedPids.Add($simProc.Id) }
    } else {
        Write-Host "  -> Bo qua Simulator (San sang ket noi voi ESP32 that)." -ForegroundColor Gray
    }
    Write-Host "----------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""

    try {
        $Host.UI.RawUI.WindowTitle = "Smart Classroom AIoT - [DANG CHAY] - Nhan Ctrl + C de DUNG"
    } catch {}

    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "   HE THONG DA SAN SANG VA DANG CHAY ON DINH!" -ForegroundColor Green
    Write-Host "   - Web Dashboard:  http://localhost:5173" -ForegroundColor White
    Write-Host "   - Backend API:    http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   - Camera Service: http://localhost:8001/docs" -ForegroundColor White
    Write-Host "   - Tai khoan mau:  admin@smartclass.local / Admin@123" -ForegroundColor White
    Write-Host ""
    Write-Host "   [Luu y] De dung toan bo he thong: Nhan Ctrl + C tai day" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    # Mo trinh duyet
    Start-Sleep -Seconds 2
    try {
        Start-Process "http://localhost:5173"
    } catch {}

    # Giu phien chay
    while ($true) {
        Start-Sleep -Seconds 1
    }

} finally {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host "  DANG DUNG TOAN BO DICH VU HE THONG (VUI LONG DOI)..." -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    # Dung cac process trees da khoi tao
    foreach ($procId in $spawnedPids) {
        try {
            taskkill.exe /F /T /PID $procId 2>$null | Out-Null
        } catch {}
    }

    # Don dep tat ca process python hoac node thuoc thu muc du an
    try {
        Get-Process python -ErrorAction SilentlyContinue | 
            Where-Object { $_.Path -like "*demo_chuong_6_lt*" } | 
            Stop-Process -Force
    } catch {}

    try {
        taskkill.exe /F /IM node.exe 2>$null | Out-Null
    } catch {}

    # Dung Docker
    Write-Host "  Dang dung Docker (PostgreSQL & Mosquitto)..." -ForegroundColor Gray
    try {
        Push-Location $infraDir
        docker compose stop 2>$null | Out-Null
        Pop-Location
    } catch {}

    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  [HOAN TAT] HE THONG DA DUOC DUNG AN TOAN VA SACH SE!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
}