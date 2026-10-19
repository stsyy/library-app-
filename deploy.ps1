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
& .venv\Scripts\pip install -r requirements.txt -q --disable-pip-version-check
Pop-Location

# 4. Запуск в фоне через WMI: процесс не входит в дерево процессов сборки,
#    поэтому Jenkins не ждёт его завершения и не убивает его после окончания job.
$cmd = "cmd.exe /c set PORT=$Port&& .venv\Scripts\python.exe run.py > app.log 2>&1"
$res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create `
    -Arguments @{ CommandLine = $cmd; CurrentDirectory = $DeployDir }
if ($res.ReturnValue -ne 0) { Write-Error "Failed to start app (code $($res.ReturnValue))"; exit 1 }
Write-Host "Started app, PID $($res.ProcessId)"

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
