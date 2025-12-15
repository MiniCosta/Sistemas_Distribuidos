# Script para verificar o status de todos os processos
param(
    [switch]$Local,
    [switch]$Kubernetes
)

Write-Host "`n=== STATUS DOS PROCESSOS ===" -ForegroundColor Cyan

if ($Kubernetes) {
    Write-Host "`nVerificando processos no Kubernetes..." -ForegroundColor Yellow
    
    # Verificar pods
    Write-Host "`nPods:" -ForegroundColor Green
    kubectl get pods -l app=leader-election
    
    # Port-forward e verificar status
    Write-Host "`nPara verificar status detalhado, use:" -ForegroundColor Yellow
    Write-Host "kubectl port-forward service/process-0 5000:5000"
    Write-Host "kubectl port-forward service/process-1 5001:5000"
    Write-Host "kubectl port-forward service/process-2 5002:5000"
    Write-Host "`nDepois execute este script com -Local"
    
} else {
    # Verificação local (padrão)
    $ports = @(5000, 5001, 5002)
    
    foreach ($port in $ports) {
        Write-Host "`n--- Processo na porta $port ---" -ForegroundColor Green
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$port/status" -Method GET -ErrorAction Stop
            
            Write-Host "Process ID: $($response.process_id)" -ForegroundColor White
            Write-Host "Is Coordinator: $($response.is_coordinator)" -ForegroundColor $(if ($response.is_coordinator) { "Green" } else { "White" })
            Write-Host "Current Coordinator: $($response.coordinator_id)" -ForegroundColor Cyan
            Write-Host "In Election: $($response.in_election)" -ForegroundColor $(if ($response.in_election) { "Yellow" } else { "White" })
            Write-Host "All Processes: $($response.all_processes -join ', ')" -ForegroundColor Gray
            
        } catch {
            Write-Host "ERRO: Processo não está respondendo" -ForegroundColor Red
            Write-Host "Detalhes: $($_.Exception.Message)" -ForegroundColor DarkRed
        }
    }
    
    Write-Host "`n=== RESUMO ===" -ForegroundColor Cyan
    Write-Host "Verifique qual processo é o coordenador atual (Is Coordinator: True)" -ForegroundColor Yellow
}

Write-Host ""
