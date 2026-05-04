# Starts backend (port 8000) and frontend (Vite) in two new windows.
# Usage (from repo root in PowerShell):
#   powershell -ExecutionPolicy Bypass -File .\run_all.ps1
#
# Put your key in backend\.env as:  GROQ_API_KEY=gsk_...
# Or set for this session before running:
#   $env:GROQ_API_KEY = "gsk_..."

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

$envFile = Join-Path $Root "backend\.env"
if (-not $env:GROQ_API_KEY -and -not (Test-Path $envFile)) {
    @"
GROQ_API_KEY=PASTE_YOUR_GROQ_KEY_HERE
JWT_SECRET=dev-secret-change-for-production
"@ | Set-Content -Path $envFile -Encoding UTF8
    Write-Host ""
    Write-Host "Created backend\.env — replace PASTE_YOUR_GROQ_KEY_HERE with your real key, then in the BACKEND window press Ctrl+C once and run the same uvicorn line again (or close and re-run this script)." -ForegroundColor Yellow
    Write-Host "Path: $envFile"
    Write-Host ""
}

$backendLines = @(
    "Set-Location -LiteralPath '$Root\backend'"
    "Write-Host '=== BACKEND (Ctrl+C to stop) ===' -ForegroundColor Cyan"
    "python -m pip install -r requirements.txt -q"
    "python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
) -join "; "

$frontendLines = @(
    "Set-Location -LiteralPath '$Root\frontend'"
    "Write-Host '=== FRONTEND (Ctrl+C to stop) ===' -ForegroundColor Magenta"
    "npm install"
    "npm run dev"
) -join "; "

Write-Host "Opening BACKEND in a new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendLines)

Start-Sleep -Seconds 2

Write-Host "Opening FRONTEND in a new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $frontendLines)

Write-Host ""
Write-Host "Done. When both are ready:" -ForegroundColor White
Write-Host "  API:    http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "  App:    http://localhost:5173  (or the port Vite prints)" -ForegroundColor Gray
Write-Host ""
Write-Host "If chat does not reply: check GROQ_API_KEY in backend\.env and restart the backend window." -ForegroundColor Yellow
