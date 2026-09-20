@echo off
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*device-simulator*' } | Stop-Process -Force"
echo [OK] Da tat bo gia lap Simulator thanh cong!
pause
