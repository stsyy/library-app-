# Доставка приложения: копирование в каталог развёртывания, перезапуск и smoke-тест.
param(
    [string]$DeployDir = "D:\course4\devops\deploy\library-app",
    [int]$Port = 5000,
    [string]$Python = "python"
)
$ErrorActionPreference = "Stop"

# 1. Остановить предыдущую версию: дерево процессов из PID-файла
#    и любые оставшиеся python-процессы, запущенные из каталога развёртывания с run.py
$pidFile = Join-Path $DeployDir "app.pid"
if (Test-Path $pidFile) {
    $oldPid = Get-Content $pidFile
    Write-Host "Stopping old instance (PID $oldPid)"
    taskkill /T /F /PID $oldPid 2>&1 | Out-Null
    Remove-Item $pidFile
}
Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" |
    Where-Object { $_.CommandLine -like "*run.py*" -and $_.CommandLine -notlike "*jenkins*" } |
    ForEach-Object { Write-Host "Stopping leftover $($_.Name) (PID $($_.ProcessId))"; Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 2

# 2. Скопировать код (база данных в каталоге развёртывания сохраняется)
New-Item -ItemType Directory -Force $DeployDir | Out-Null
Copy-Item -Recurse -Force app, run.py, requirements.txt $DeployDir

# 3. Окружение и зависимости
Push-Location $DeployDir
if (-not (Test-Path .venv)) { & $Python -m venv .venv }
& .venv\Scripts\pip install -r requirements.txt -q --disable-pip-version-check
Pop-Location

# 4. Запуск в фоне. Start-Process без -Redirect* не наследует дескрипторы вывода,
#    поэтому шаг Jenkins не ждёт приложение; JENKINS_NODE_COOKIE не даёт Jenkins
#    убить процесс после окончания сборки.
$env:JENKINS_NODE_COOKIE = "dontKillMe"
$env:PORT = "$Port"
$proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", ".venv\Scripts\python.exe run.py > app.log 2>&1" `
    -WorkingDirectory $DeployDir -WindowStyle Hidden -PassThru
Set-Content -Path $pidFile -Value $proc.Id
Write-Host "Started app, PID $($proc.Id)"

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
