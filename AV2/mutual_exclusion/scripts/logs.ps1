# Script para visualizar logs em tempo real
# AV2 - Exclusão Mútua Distribuída

param(
    [ValidateSet("coordinator", "process", "all")]
    [string]$Component = "all"
)

$NAMESPACE = "mutual-exclusion"

Write-Host "`n=== 📋 LOGS - EXCLUSÃO MÚTUA DISTRIBUÍDA ===" -ForegroundColor Cyan
Write-Host ""

if ($Component -eq "coordinator" -or $Component -eq "all") {
    Write-Host "📊 Logs do Coordinator:" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    kubectl logs -n $NAMESPACE -l app=coordinator --tail=50 -f
}

if ($Component -eq "process") {
    Write-Host "🔄 Logs dos Processes:" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    kubectl logs -n $NAMESPACE -l app=process --tail=50 -f --prefix=true
}
