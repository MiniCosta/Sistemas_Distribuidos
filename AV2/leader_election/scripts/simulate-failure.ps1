# Script para simular falha de um processo
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(0, 1, 2)]
    [int]$ProcessId,
    
    [switch]$Kubernetes
)

Write-Host "`n=== SIMULANDO FALHA DO PROCESSO $ProcessId ===" -ForegroundColor Red

if ($Kubernetes) {
    Write-Host "`nDeletando pod do processo $ProcessId no Kubernetes..." -ForegroundColor Yellow
    
    kubectl delete pod -l process-id="$ProcessId"
    
    Write-Host "`nPod deletado! O Kubernetes irá recriar automaticamente." -ForegroundColor Green
    Write-Host "Aguarde alguns segundos e verifique o status:" -ForegroundColor Yellow
    Write-Host ".\scripts\check-status.ps1 -Kubernetes" -ForegroundColor Cyan
    
} else {
    # Simular falha local
    $port = 5000 + $ProcessId
    
    Write-Host "`nTentando parar o processo na porta $port..." -ForegroundColor Yellow
    
    try {
        # Encontrar e parar o processo Python na porta específica
        $netstatOutput = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
        
        if ($netstatOutput) {
            $pid = ($netstatOutput -split '\s+')[-1]
            
            Write-Host "Encontrado PID: $pid" -ForegroundColor White
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Host "Processo $ProcessId (PID: $pid) foi parado!" -ForegroundColor Green
        } else {
            Write-Host "AVISO: Nenhum processo encontrado na porta $port" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "ERRO ao parar processo: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`nVerifique o status dos processos:" -ForegroundColor Yellow
    Write-Host ".\scripts\check-status.ps1" -ForegroundColor Cyan
    
    Write-Host "`nOs outros processos devem detectar a falha e iniciar uma eleição automaticamente." -ForegroundColor Yellow
}

Write-Host ""
