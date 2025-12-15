# Script PowerShell para teste local (Windows)
# Executa 3 processos localmente para testes antes de subir no Kubernetes

param(
    [switch]$DelayMode = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "  Multicast com Ordenacao Total - Local  "
Write-Host "=========================================="

# Mata processos anteriores
Write-Host "`n Parando processos anteriores..."
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Define variáveis de ambiente
$env:NUM_PROCESSES = "3"
$env:PROCESS_0_URL = "http://localhost:5000"
$env:PROCESS_1_URL = "http://localhost:5001"
$env:PROCESS_2_URL = "http://localhost:5002"

if ($DelayMode) {
    Write-Host "`n MODO DE DELAY ATIVADO!"
    $env:DELAY_MODE = "true"
} else {
    $env:DELAY_MODE = "false"
}

# Inicia os 3 processos em terminais separados
Write-Host "`n Iniciando 3 processos..."

# Processo 0 - Porta 5000
$p0Script = @"
`$env:PROCESS_ID = '0'
`$env:NUM_PROCESSES = '3'
`$env:PROCESS_0_URL = 'http://localhost:5000'
`$env:PROCESS_1_URL = 'http://localhost:5001'
`$env:PROCESS_2_URL = 'http://localhost:5002'
`$env:DELAY_MODE = '$($env:DELAY_MODE)'
cd '$PSScriptRoot\..'
python app.py
"@

# Processo 1 - Porta 5001
$p1Script = @"
`$env:PROCESS_ID = '1'
`$env:PORT = '5001'
`$env:NUM_PROCESSES = '3'
`$env:PROCESS_0_URL = 'http://localhost:5000'
`$env:PROCESS_1_URL = 'http://localhost:5001'
`$env:PROCESS_2_URL = 'http://localhost:5002'
    $env:DELAY_MODE = '$($env:DELAY_MODE)'
`$env:DELAY_PROCESS = '1'
`$env:DELAY_SECONDS = '10'
cd '$PSScriptRoot\..'
python app.py
"@

# Processo 2 - Porta 5002
$p2Script = @"
`$env:PROCESS_ID = '2'
`$env:PORT = '5002'
`$env:NUM_PROCESSES = '3'
`$env:PROCESS_0_URL = 'http://localhost:5000'
`$env:PROCESS_1_URL = 'http://localhost:5001'
`$env:PROCESS_2_URL = 'http://localhost:5002'
`$env:DELAY_MODE = '$($env:DELAY_MODE)'
cd '$PSScriptRoot\..'
python app.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $p0Script
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", $p1Script
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", $p2Script

Write-Host "`n Aguardando processos iniciarem..."
Start-Sleep -Seconds 3

Write-Host "`n=========================================="
Write-Host "  Processos iniciados!                   "
Write-Host "=========================================="
Write-Host ""
Write-Host "Endpoints disponiveis:"
Write-Host "  P0: http://localhost:5000"
Write-Host "  P1: http://localhost:5001"
Write-Host "  P2: http://localhost:5002"
Write-Host ""
Write-Host "Para enviar mensagem:"
Write-Host "  Invoke-RestMethod -Uri 'http://localhost:5000/send' -Method Post -ContentType 'application/json' -Body '{""content"": ""Teste""}'"
Write-Host ""
Write-Host "Para ver status:"
Write-Host "  Invoke-RestMethod -Uri 'http://localhost:5000/status'"
