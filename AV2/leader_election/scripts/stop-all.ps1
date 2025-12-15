# Script para parar todos os processos locais
Write-Host "`n=== PARANDO TODOS OS PROCESSOS ===" -ForegroundColor Red

Write-Host "`nProcurando processos Python..." -ForegroundColor Yellow

try {
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
    
    if ($pythonProcesses) {
        Write-Host "Encontrados $($pythonProcesses.Count) processo(s) Python" -ForegroundColor White
        
        foreach ($proc in $pythonProcesses) {
            Write-Host "Parando PID: $($proc.Id)" -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
        
        Write-Host "`nTodos os processos foram parados!" -ForegroundColor Green
    } else {
        Write-Host "Nenhum processo Python em execução" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
