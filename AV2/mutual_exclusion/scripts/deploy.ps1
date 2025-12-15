# Script de Deploy para Kubernetes/Minikube
# AV2 - Exclusão Mútua Distribuída

param(
    [switch]$Build = $false,
    [switch]$Apply = $false,
    [switch]$All = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== 🚀 DEPLOY - EXCLUSÃO MÚTUA DISTRIBUÍDA ===" -ForegroundColor Cyan
Write-Host "Algoritmo: Centralizado" -ForegroundColor Green
Write-Host ""

$PROJECT_ROOT = $PSScriptRoot | Split-Path
$NAMESPACE = "mutual-exclusion"

# Função para verificar se Minikube está rodando
function Test-Minikube {
    try {
        $status = minikube status --format='{{.Host}}' 2>$null
        return $status -eq "Running"
    }
    catch {
        return $false
    }
}

# Função para construir imagens Docker
function Build-Images {
    Write-Host "`n📦 Construindo imagens Docker..." -ForegroundColor Yellow
    
    # Configurar Docker para usar o daemon do Minikube
    Write-Host "Configurando Docker para Minikube..." -ForegroundColor Cyan
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression
    
    # Build Coordinator
    Write-Host "`n🏗️  Building Coordinator..." -ForegroundColor Cyan
    docker build -t mutual-exclusion-coordinator:latest "$PROJECT_ROOT\coordinator"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao construir imagem do Coordinator" -ForegroundColor Red
        exit 1
    }
    
    # Build Process
    Write-Host "`n🏗️  Building Process..." -ForegroundColor Cyan
    docker build -t mutual-exclusion-process:latest "$PROJECT_ROOT\process"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao construir imagem do Process" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`n✅ Imagens construídas com sucesso!" -ForegroundColor Green
}

# Função para aplicar recursos no Kubernetes
function Apply-K8sResources {
    Write-Host "`n☸️  Aplicando recursos no Kubernetes..." -ForegroundColor Yellow
    
    # Criar namespace
    Write-Host "Criando namespace..." -ForegroundColor Cyan
    kubectl apply -f "$PROJECT_ROOT\k8s\namespace.yaml"
    
    # Deploy Coordinator
    Write-Host "Deployando Coordinator..." -ForegroundColor Cyan
    kubectl apply -f "$PROJECT_ROOT\k8s\coordinator.yaml"
    
    # Deploy Processes
    Write-Host "Deployando Processes..." -ForegroundColor Cyan
    kubectl apply -f "$PROJECT_ROOT\k8s\process.yaml"
    
    Write-Host "`n✅ Recursos aplicados com sucesso!" -ForegroundColor Green
}

# Verificar se Minikube está rodando
Write-Host "🔍 Verificando Minikube..." -ForegroundColor Cyan
if (-not (Test-Minikube)) {
    Write-Host "⚠️  Minikube não está rodando!" -ForegroundColor Yellow
    Write-Host "Iniciando Minikube..." -ForegroundColor Cyan
    minikube start --driver=docker
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao iniciar Minikube" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Minikube está rodando" -ForegroundColor Green

# Executar ações baseado nos parâmetros
if ($All) {
    Build-Images
    Apply-K8sResources
}
elseif ($Build) {
    Build-Images
}
elseif ($Apply) {
    Apply-K8sResources
}
else {
    # Default: fazer tudo
    Build-Images
    Apply-K8sResources
}

# Aguardar pods ficarem prontos
Write-Host "`n⏳ Aguardando pods ficarem prontos..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=coordinator -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=process -n $NAMESPACE --timeout=120s

# Mostrar status
Write-Host "`n📊 Status dos Pods:" -ForegroundColor Cyan
kubectl get pods -n $NAMESPACE -o wide

Write-Host "`n📊 Status dos Services:" -ForegroundColor Cyan
kubectl get services -n $NAMESPACE

# Instruções
Write-Host "`n✨ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "`n📝 Comandos úteis:" -ForegroundColor Cyan
Write-Host "  Ver logs do coordinator:" -ForegroundColor White
Write-Host "    kubectl logs -n $NAMESPACE -l app=coordinator -f" -ForegroundColor Gray
Write-Host ""
Write-Host "  Ver logs dos processes:" -ForegroundColor White
Write-Host "    kubectl logs -n $NAMESPACE -l app=process -f" -ForegroundColor Gray
Write-Host ""
Write-Host "  Verificar status:" -ForegroundColor White
Write-Host "    kubectl get pods -n $NAMESPACE" -ForegroundColor Gray
Write-Host ""
Write-Host "  Testar a aplicação:" -ForegroundColor White
Write-Host "    .\scripts\test.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  Limpar recursos:" -ForegroundColor White
Write-Host "    .\scripts\cleanup.ps1" -ForegroundColor Gray
Write-Host ""
