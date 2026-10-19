# Доставка приложения: копирование в каталог развёртывания, перезапуск и smoke-тест.
param(
    [string]$DeployDir = "D:\course4\devops\deploy\library-app",
    [int]$Port = 5000,
    [string]$Python = "python"
)
$ErrorActionPreference = "Stop"

# 1. Остановить предыдущую версию, если запущена
$old = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($old) {
    Write-Host "Stopping old instance (PID $($old.OwningProcess))"
    Stop-Process -Id $old.OwningProcess -Force
    Start-Sleep -Seconds 2
}

# 2. Скопировать код (база данных в каталоге развёртывания сохраняется)
New-Item -ItemType Directory -Force $DeployDir | Out-Null
Copy-Item -Recurse -Force app, run.py, requirements.txt $DeployDir

# 3. Окружение и зависимости
Push-Location $DeployDir
if (-not (Test-Path .venv)) { & $Python -m venv .venv }
& .venv\Scripts\pip install -r requirements.txt -q

# 4. Запуск в фоне. JENKINS_NODE_COOKIE не даёт Jenkins убить процесс после сборки.
$env:JENKINS_NODE_COOKIE = "dontKillMe"
$env:PORT = "$Port"
Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "run.py" -WorkingDirectory $DeployDir `
    -WindowStyle Hidden -RedirectStandardOutput app.log -RedirectStandardError app.err.log
Pop-Location

# 5. Smoke-тест
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-RestMethod "http://localhost:$Port/api/health"
        if ($r.status -eq "ok") { Write-Host "Deployed: http://localhost:$Port/api/health -> ok"; exit 0 }
    } catch {}
}
Write-Error "Smoke test failed"
exit 1
