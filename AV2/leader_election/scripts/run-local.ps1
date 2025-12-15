# Script para executar os 3 processos localmente
Write-Host "`n=== INICIANDO PROCESSOS LOCALMENTE ===" -ForegroundColor Cyan

# Verificar se Python está disponível
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado no PATH" -ForegroundColor Red
    Write-Host "Instale o Python 3.11+ antes de continuar" -ForegroundColor Yellow
    exit 1
}

# Verificar se as dependências estão instaladas
Write-Host "`nVerificando dependências..." -ForegroundColor Yellow

$requirementsFile = Join-Path $PSScriptRoot "..\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    pip install -r $requirementsFile --quiet
    Write-Host "Dependências instaladas!" -ForegroundColor Green
} else {
    Write-Host "AVISO: requirements.txt não encontrado" -ForegroundColor Yellow
}

# Parar processos anteriores
Write-Host "`nParando processos anteriores..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Diretório src
$srcDir = Join-Path $PSScriptRoot "..\src"

# Iniciar Processo 0
Write-Host "`nIniciando Processo 0 (porta 5000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:PROCESS_ID='0'; `$env:PORT='5000'; Set-Location '$srcDir'; python process.py"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# Iniciar Processo 1
Write-Host "Iniciando Processo 1 (porta 5001)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:PROCESS_ID='1'; `$env:PORT='5001'; Set-Location '$srcDir'; python process.py"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# Iniciar Processo 2
Write-Host "Iniciando Processo 2 (porta 5002)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:PROCESS_ID='2'; `$env:PORT='5002'; Set-Location '$srcDir'; python process.py"
) -WindowStyle Normal

Write-Host "`n=== PROCESSOS INICIADOS ===" -ForegroundColor Green
Write-Host "`nAguarde alguns segundos para os processos iniciarem completamente..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`nVerificando status..." -ForegroundColor Cyan
& "$PSScriptRoot\check-status.ps1"

Write-Host "`n=== COMANDOS ÚTEIS ===" -ForegroundColor Yellow
Write-Host "Verificar status:     .\scripts\check-status.ps1" -ForegroundColor White
Write-Host "Simular falha:        .\scripts\simulate-failure.ps1 -ProcessId 2" -ForegroundColor White
Write-Host "Forçar eleição:       Invoke-RestMethod -Uri http://localhost:5000/trigger-election -Method POST" -ForegroundColor White
Write-Host "Parar processos:      .\scripts\stop-all.ps1" -ForegroundColor White

Write-Host ""
