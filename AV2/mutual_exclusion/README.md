# Exclusão Mútua Distribuída - Algoritmo Centralizado

## Visão Geral

Implementação do algoritmo de **Exclusão Mútua Centralizada** para a AV2 de Sistemas Distribuídos.

### Algoritmo Escolhido: Centralizado

**Por que escolhi o algoritmo centralizado?**

- ✅ **Menor complexidade**: O(2) mensagens por entrada na região crítica
- ✅ **Garantia de exclusão mútua**: Apenas um processo por vez
- ✅ **Fairness**: FIFO queue garante justiça
- ✅ **Simplicidade**: Fácil de entender e depurar

### Comparação de Complexidade (mensagens por entrada na RC)

1. **Token Ring**: O(1) a O(n) - melhor caso quando tem o token
2. **Centralizado**: O(2) - REQUEST + GRANT (escolhido)
3. **Descentralizado**: O(3√n) - votação com múltiplos coordenadores
4. **Distribuído (Ricart-Agrawala)**: O(2(n-1)) - multicast para todos

## Arquitetura

```
┌─────────────────┐
│  Coordenador    │  (coordinator service)
│  (Centralizado) │  - Gerencia fila de requisições
│                 │  - Concede acesso à RC
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│Process│ │Process│ │Process│ │Process│
│   0   │ │   1   │ │   2   │ │   3   │
└───────┘ └──────┘ └──────┘ └──────┘
```

### Funcionamento

1. **REQUEST**: Processo envia requisição ao coordenador
2. **QUEUE**: Coordenador adiciona à fila FIFO
3. **GRANT**: Coordenador concede acesso quando disponível
4. **RELEASE**: Processo libera a região crítica
5. **NEXT**: Coordenador concede ao próximo da fila

## Estrutura do Projeto

```
mutual_exclusion/
├── coordinator/
│   ├── app.py              # Servidor coordenador
│   ├── requirements.txt
│   └── Dockerfile
├── process/
│   ├── app.py              # Processo cliente
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── coordinator.yaml    # Deployment do coordenador
│   ├── process.yaml        # Deployment dos processos
│   └── namespace.yaml
├── scripts/
│   ├── deploy.ps1          # Deploy no Minikube
│   ├── test.ps1            # Testes de exclusão mútua
│   └── cleanup.ps1         # Limpeza dos recursos
└── README.md
```

## Pré-requisitos

- Docker Desktop
- Minikube
- kubectl
- Python 3.9+

## Como Executar

### 1. Iniciar Minikube

```powershell
minikube start --driver=docker
```

### 2. Deploy da Aplicação

```powershell
.\scripts\deploy.ps1
```

### 3. Verificar Pods

```powershell
kubectl get pods -n mutual-exclusion
```

### 4. Testar Exclusão Mútua

```powershell
.\scripts\test.ps1
```

### 5. Ver Logs

```powershell
# Logs do coordenador
kubectl logs -n mutual-exclusion -l app=coordinator -f

# Logs dos processos
kubectl logs -n mutual-exclusion -l app=process -f
```

### 6. Limpar Recursos

```powershell
.\scripts\cleanup.ps1
```

## Endpoints da API

### Coordenador (port 5000)

- `POST /request` - Requisitar acesso à RC
- `POST /release` - Liberar a RC
- `GET /status` - Status do coordenador
- `GET /metrics` - Métricas de performance

### Processo (port 8080)

- `GET /status` - Status do processo
- `POST /trigger` - Forçar requisição de RC
- `GET /history` - Histórico de acessos

## Demonstração

A aplicação simula processos competindo por uma região crítica (arquivo compartilhado).
Cada processo:

1. Requisita acesso ao coordenador
2. Aguarda permissão (GRANT)
3. Executa operação na RC (incrementa contador)
4. Libera a RC
5. Repete após intervalo aleatório

## Verificação de Corretude

O sistema garante:

- ✅ **Exclusão Mútua**: Apenas 1 processo por vez na RC
- ✅ **Progresso**: Sempre há um próximo processo
- ✅ **Fairness**: FIFO garante que todos acessam
- ✅ **Sem Deadlock**: Coordenador gerencia liberações

## Métricas Coletadas

- Número de requisições processadas
- Tempo médio de espera
- Número de processos na fila
- Taxa de throughput

## Autor

Paulo - AV2 Sistemas Distribuídos 2025.2
