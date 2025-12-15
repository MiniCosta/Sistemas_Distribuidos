# Leader Election - Algoritmo do Valentão (Bully)

Este projeto implementa o algoritmo de eleição de líder "Bully" (Valentão) usando Python Flask com REST API e deployment no Kubernetes.

## 🎯 Descrição

Sistema distribuído que implementa eleição de líder onde:

- Cada processo possui um ID único
- Processos podem detectar falhas do coordenador
- Processos com IDs maiores têm prioridade na eleição
- API REST para comunicação entre processos

## 🏗️ Arquitetura

- **Algoritmo**: Bully (Valentão)
- **Linguagem**: Python 3.11+
- **Framework**: Flask
- **Orquestração**: Kubernetes (Minikube)

## 📋 Endpoints da API

### GET /status

Retorna o status atual do processo

```json
{
  "process_id": 1,
  "is_coordinator": false,
  "coordinator_id": 2,
  "state": "active"
}
```

### POST /election

Inicia uma eleição

```json
{
  "from_process": 0
}
```

### POST /coordinator

Anuncia o novo coordenador

```json
{
  "coordinator_id": 2
}
```

### POST /answer

Responde a uma mensagem de eleição

```json
{
  "from_process": 2
}
```

### GET /health

Health check para Kubernetes

## 🚀 Execução Local (Desenvolvimento)

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

```powershell
pip install -r requirements.txt
```

### Executar processos localmente

```powershell
# Terminal 1
$env:PROCESS_ID="0"; $env:PORT="5000"; python src/process.py

# Terminal 2
$env:PROCESS_ID="1"; $env:PORT="5001"; python src/process.py

# Terminal 3
$env:PROCESS_ID="2"; $env:PORT="5002"; python src/process.py
```

### Testar eleição

```powershell
# Simular falha do coordenador (processo 2)
# Fechar o terminal do processo 2

# Iniciar eleição do processo 0
Invoke-RestMethod -Uri http://localhost:5000/election -Method POST -ContentType "application/json" -Body '{"from_process": 0}'
```

## ☸️ Deployment no Kubernetes (Minikube)

### Pré-requisitos

- Docker Desktop
- Minikube
- kubectl

### 1. Iniciar Minikube

```powershell
minikube start
```

### 2. Configurar Docker para usar Minikube

```powershell
minikube docker-env | Invoke-Expression
```

### 3. Build da imagem Docker

```powershell
docker build -t leader-election:latest .
```

### 4. Deploy no Kubernetes

```powershell
kubectl apply -f k8s/
```

### 5. Verificar pods

```powershell
kubectl get pods -l app=leader-election
kubectl get services
```

### 6. Acessar a aplicação

```powershell
# Port-forward para acessar os processos
kubectl port-forward service/process-0 5000:5000
kubectl port-forward service/process-1 5001:5000
kubectl port-forward service/process-2 5002:5000
```

### 7. Testar eleição

```powershell
# Verificar status
Invoke-RestMethod -Uri http://localhost:5000/status

# Iniciar eleição
Invoke-RestMethod -Uri http://localhost:5000/election -Method POST -ContentType "application/json" -Body '{"from_process": 0}'
```

### 8. Simular falha

```powershell
# Deletar pod do coordenador
kubectl delete pod -l process-id=2

# Verificar nova eleição automática
Invoke-RestMethod -Uri http://localhost:5000/status
```

### 9. Limpar recursos

```powershell
kubectl delete -f k8s/
minikube stop
```

## 📊 Funcionamento do Algoritmo Bully

1. **Detecção de Falha**: Quando um processo detecta que o coordenador falhou
2. **Início da Eleição**: Processo envia mensagem ELECTION para todos com ID maior
3. **Resposta**: Processos com ID maior respondem com ANSWER
4. **Novo Coordenador**: Se ninguém responder, processo se torna coordenador
5. **Anúncio**: Novo coordenador envia mensagem COORDINATOR para todos

## 🧪 Scripts de Teste

```powershell
# Verificar status de todos os processos
.\scripts\check-status.ps1

# Simular falha de um processo
.\scripts\simulate-failure.ps1 -ProcessId 2

# Parar todos os processos locais
.\scripts\stop-all.ps1
```

## 📝 Estrutura do Projeto

```
leader_election/
├── src/
│   ├── process.py          # Implementação do processo
│   └── bully_algorithm.py  # Lógica do algoritmo Bully
├── k8s/
│   ├── process-0.yaml      # Deployment processo 0
│   ├── process-1.yaml      # Deployment processo 1
│   ├── process-2.yaml      # Deployment processo 2
│   └── services.yaml       # Services
├── scripts/
│   ├── check-status.ps1    # Verificar status
│   ├── simulate-failure.ps1 # Simular falha
│   └── stop-all.ps1        # Parar processos
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔍 Logs e Debug

```powershell
# Ver logs de um pod específico
kubectl logs -l process-id=0

# Ver logs em tempo real
kubectl logs -f -l app=leader-election

# Descrever pod
kubectl describe pod -l process-id=0
```

## 📚 Referências

- [Algoritmo Bully](https://en.wikipedia.org/wiki/Bully_algorithm)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
