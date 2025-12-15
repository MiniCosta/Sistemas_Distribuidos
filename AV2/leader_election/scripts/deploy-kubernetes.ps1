# Script para deploy completo no Kubernetes (Minikube)
Write-Host "`n=== DEPLOY NO KUBERNETES (MINIKUBE) ===" -ForegroundColor Cyan

# Verificar se Minikube está instalado
Write-Host "`n1. Verificando Minikube..." -ForegroundColor Yellow
try {
    $minikubeVersion = minikube version 2>&1
    Write-Host "Minikube encontrado!" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Minikube não encontrado" -ForegroundColor Red
    Write-Host "Instale o Minikube: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    exit 1
}

# Verificar se Minikube está rodando
Write-Host "`n2. Verificando status do Minikube..." -ForegroundColor Yellow
$minikubeStatus = minikube status 2>&1

if ($minikubeStatus -match "Running") {
    Write-Host "Minikube já está rodando!" -ForegroundColor Green
} else {
    Write-Host "Iniciando Minikube..." -ForegroundColor Yellow
    minikube start
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao iniciar Minikube" -ForegroundColor Red
        exit 1
    }
    Write-Host "Minikube iniciado!" -ForegroundColor Green
}

# Configurar Docker para usar Minikube
Write-Host "`n3. Configurando Docker para usar Minikube..." -ForegroundColor Yellow
minikube docker-env | Invoke-Expression
Write-Host "Docker configurado para Minikube!" -ForegroundColor Green

# Build da imagem Docker
Write-Host "`n4. Construindo imagem Docker..." -ForegroundColor Yellow
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

docker build -t leader-election:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao construir imagem Docker" -ForegroundColor Red
    exit 1
}
Write-Host "Imagem construída com sucesso!" -ForegroundColor Green

# Deploy no Kubernetes
Write-Host "`n5. Fazendo deploy no Kubernetes..." -ForegroundColor Yellow
kubectl apply -f k8s/

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao fazer deploy" -ForegroundColor Red
    exit 1
}
Write-Host "Deploy realizado!" -ForegroundColor Green

# Aguardar pods ficarem prontos
Write-Host "`n6. Aguardando pods ficarem prontos..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=leader-election --timeout=60s

# Mostrar status
Write-Host "`n=== STATUS DO DEPLOYMENT ===" -ForegroundColor Cyan
Write-Host "`nPods:" -ForegroundColor Green
kubectl get pods -l app=leader-election

Write-Host "`nServices:" -ForegroundColor Green
kubectl get services -l app=leader-election

# Instruções de uso
Write-Host "`n=== COMO USAR ===" -ForegroundColor Yellow
Write-Host "`n1. Fazer port-forward dos serviços (em terminais separados):"
Write-Host "   kubectl port-forward service/process-0 5000:5000" -ForegroundColor Cyan
Write-Host "   kubectl port-forward service/process-1 5001:5000" -ForegroundColor Cyan
Write-Host "   kubectl port-forward service/process-2 5002:5000" -ForegroundColor Cyan

Write-Host "`n2. Verificar status:"
Write-Host "   .\scripts\check-status.ps1" -ForegroundColor Cyan

Write-Host "`n3. Simular falha de um processo:"
Write-Host "   .\scripts\simulate-failure.ps1 -ProcessId 2 -Kubernetes" -ForegroundColor Cyan

Write-Host "`n4. Ver logs:"
Write-Host "   kubectl logs -l process-id=0" -ForegroundColor Cyan
Write-Host "   kubectl logs -f -l app=leader-election" -ForegroundColor Cyan

Write-Host "`n5. Limpar recursos:"
Write-Host "   kubectl delete -f k8s/" -ForegroundColor Cyan
Write-Host "   minikube stop" -ForegroundColor Cyan

Write-Host ""
