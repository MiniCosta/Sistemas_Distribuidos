# Testes Locais (sem Kubernetes)
# Útil para desenvolvimento e debug

param(
    [switch]$Coordinator = $false,
    [switch]$Process = $false,
    [int]$ProcessCount = 3
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== 🧪 TESTE LOCAL - EXCLUSÃO MÚTUA ===" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ROOT = $PSScriptRoot | Split-Path

function Start-Coordinator {
    Write-Host "🎯 Iniciando Coordinator na porta 5000..." -ForegroundColor Yellow
    
    Set-Location "$PROJECT_ROOT\coordinator"
    
    # Verificar se venv existe
    if (-not (Test-Path "venv")) {
        Write-Host "Criando ambiente virtual..." -ForegroundColor Cyan
        python -m venv venv
    }
    
    # Ativar venv e instalar dependências
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt -q
    
    # Iniciar coordinator
    python app.py
}

function Start-Process {
    param([int]$Id)
    
    Write-Host "🔄 Iniciando Process #$Id na porta $Port..." -ForegroundColor Yellow
    
    $Port = 8080 + $Id
    
    Set-Location "$PROJECT_ROOT\process"
    
    # Verificar se venv existe
    if (-not (Test-Path "venv")) {
        Write-Host "Criando ambiente virtual..." -ForegroundColor Cyan
        python -m venv venv
    }
    
    # Ativar venv e instalar dependências
    .\venv\Scripts\Activate.ps1
    pip install -q -r requirements.txt
    
    # Configurar variáveis de ambiente
    $env:PROCESS_ID = "process-$Id"
    $env:COORDINATOR_URL = "http://localhost:5000"
    $env:CS_DURATION = "2"
    $env:INTERVAL_MIN = "3"
    $env:INTERVAL_MAX = "8"
    
    # Iniciar process
    uvicorn app:app --host 0.0.0.0 --port $Port
}

# Menu interativo
if (-not $Coordinator -and -not $Process) {
    Write-Host "Escolha o componente para iniciar:" -ForegroundColor Cyan
    Write-Host "1. Coordinator" -ForegroundColor White
    Write-Host "2. Process" -ForegroundColor White
    Write-Host "3. Tudo (em terminais separados)" -ForegroundColor White
    $choice = Read-Host "`nOpção"
    
    switch ($choice) {
        "1" { Start-Coordinator }
        "2" { 
            $id = Read-Host "ID do processo (0-9)"
            Start-Process -Id $id 
        }
        "3" {
            Write-Host "`n📋 Instruções:" -ForegroundColor Yellow
            Write-Host "Execute em terminais separados:" -ForegroundColor White
            Write-Host ""
            Write-Host "Terminal 1 (Coordinator):" -ForegroundColor Cyan
            Write-Host "  .\scripts\run-local.ps1 -Coordinator" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Terminal 2, 3, 4... (Processes):" -ForegroundColor Cyan
            Write-Host "  .\scripts\run-local.ps1 -Process -Id 0" -ForegroundColor Gray
            Write-Host "  .\scripts\run-local.ps1 -Process -Id 1" -ForegroundColor Gray
            Write-Host "  .\scripts\run-local.ps1 -Process -Id 2" -ForegroundColor Gray
            Write-Host ""
        }
    }
}
elseif ($Coordinator) {
    Start-Coordinator
}
elseif ($Process) {
    $Id = Read-Host "ID do processo (0-9)"
    Start-Process -Id $Id
}
