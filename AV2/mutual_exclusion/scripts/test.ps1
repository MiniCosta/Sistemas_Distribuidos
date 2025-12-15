# Script de Teste para Exclusão Mútua Distribuída
# AV2 - Sistemas Distribuídos

$ErrorActionPreference = "Stop"

Write-Host "`n=== 🧪 TESTE - EXCLUSÃO MÚTUA DISTRIBUÍDA ===" -ForegroundColor Cyan
Write-Host ""

$NAMESPACE = "mutual-exclusion"

# Função para fazer port-forward
function Start-PortForward {
    param([string]$Service, [int]$Port)
    
    Write-Host "🔗 Iniciando port-forward para $Service..." -ForegroundColor Cyan
    $job = Start-Job -ScriptBlock {
        param($ns, $svc, $port)
        kubectl port-forward -n $ns "svc/$svc" "${port}:${port}"
    } -ArgumentList $NAMESPACE, $Service, $Port
    
    Start-Sleep -Seconds 3
    return $job
}

# Função para verificar status do coordenador
function Get-CoordinatorStatus {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/status" -Method Get
        return $response
    }
    catch {
        Write-Host "⚠️  Erro ao obter status: $_" -ForegroundColor Yellow
        return $null
    }
}

# Função para obter métricas
function Get-CoordinatorMetrics {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/metrics" -Method Get
        return $response
    }
    catch {
        Write-Host "⚠️  Erro ao obter métricas: $_" -ForegroundColor Yellow
        return $null
    }
}

# Verificar se pods estão rodando
Write-Host "🔍 Verificando pods..." -ForegroundColor Cyan
$pods = kubectl get pods -n $NAMESPACE --no-headers
Write-Host $pods
Write-Host ""

# Iniciar port-forward para o coordenador
Write-Host "🔗 Configurando port-forward para coordinator..." -ForegroundColor Yellow
$coordJob = Start-PortForward -Service "coordinator" -Port 5000

try {
    # Aguardar um pouco para os processos começarem
    Write-Host "`n⏳ Aguardando processos iniciarem (15s)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Loop de monitoramento
    Write-Host "`n📊 Monitorando exclusão mútua (pressione Ctrl+C para sair)..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $iteration = 0
    while ($true) {
        $iteration++
        
        # Obter status
        $status = Get-CoordinatorStatus
        
        if ($status) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            
            Write-Host "`n[$timestamp] Iteração #$iteration" -ForegroundColor White
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
            
            # Holder atual
            if ($status.current_holder) {
                Write-Host "🔒 Região Crítica: " -NoNewline -ForegroundColor Yellow
                Write-Host $status.current_holder -ForegroundColor Green
            }
            else {
                Write-Host "💤 Região Crítica: LIVRE" -ForegroundColor Gray
            }
            
            # Fila
            Write-Host "📋 Fila: " -NoNewline -ForegroundColor Cyan
            if ($status.queue_size -gt 0) {
                Write-Host "$($status.queue_size) processos" -ForegroundColor Yellow
                $status.queue | ForEach-Object {
                    Write-Host "   ↳ $_" -ForegroundColor Gray
                }
            }
            else {
                Write-Host "vazia" -ForegroundColor Gray
            }
            
            # Estatísticas
            Write-Host ""
            Write-Host "📈 Estatísticas:" -ForegroundColor Magenta
            Write-Host "   Requisições: $($status.total_requests)" -ForegroundColor White
            Write-Host "   Concessões:  $($status.total_grants)" -ForegroundColor White
            Write-Host "   Liberações:  $($status.total_releases)" -ForegroundColor White
        }
        
        # A cada 5 iterações, mostrar métricas detalhadas
        if ($iteration % 5 -eq 0) {
            $metrics = Get-CoordinatorMetrics
            
            if ($metrics) {
                Write-Host ""
                Write-Host "⚡ Métricas de Performance:" -ForegroundColor Yellow
                Write-Host "   Tempo médio de espera: $([math]::Round($metrics.avg_wait_time, 2))s" -ForegroundColor White
                Write-Host "   Tamanho atual da fila: $($metrics.current_queue_size)" -ForegroundColor White
            }
        }
        
        # Aguardar antes da próxima iteração
        Start-Sleep -Seconds 3
    }
}
finally {
    # Limpar port-forwards
    Write-Host "`n🧹 Limpando port-forwards..." -ForegroundColor Cyan
    Stop-Job -Job $coordJob -ErrorAction SilentlyContinue
    Remove-Job -Job $coordJob -ErrorAction SilentlyContinue
    
    Write-Host "✅ Teste finalizado" -ForegroundColor Green
}
