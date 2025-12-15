# Script de Limpeza para Exclusão Mútua Distribuída
# Remove todos os recursos do Kubernetes

$ErrorActionPreference = "Stop"

Write-Host "`n=== 🧹 CLEANUP - EXCLUSÃO MÚTUA DISTRIBUÍDA ===" -ForegroundColor Cyan
Write-Host ""

$NAMESPACE = "mutual-exclusion"

# Deletar recursos
Write-Host "🗑️  Deletando recursos do namespace $NAMESPACE..." -ForegroundColor Yellow

kubectl delete namespace $NAMESPACE --ignore-not-found=true

Write-Host ""
Write-Host "⏳ Aguardando namespace ser removido..." -ForegroundColor Cyan
kubectl wait --for=delete namespace/$NAMESPACE --timeout=60s 2>$null

Write-Host ""
Write-Host "✅ Limpeza concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "Para fazer novo deploy:" -ForegroundColor Cyan
Write-Host "  .\scripts\deploy.ps1" -ForegroundColor White
Write-Host ""
